import csv
import time
from pathlib import Path
from datetime import datetime
from rich.live import Live
from rich.table import Table, Column

from early.display.base import BaseDisplay


class Display(BaseDisplay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__csv_file_path = None

    @property
    def csv_file_path(self):
        if self.__csv_file_path is None:
            # Defining the path of the CSV file
            self.__csv_file_path = Path.cwd() / f"display_flows_{time.strftime('%m%d-%H%M%S')}.csv"

            print(f"Dumping flows to {self.__csv_file_path}")
        return self.__csv_file_path

    def write_csv_line(self, data):
        flows_dump = []
        for key in data:
            f = {"updated_at": datetime.fromtimestamp(data[key]['last_updated']),
                 "name": data[key]['name'],
                 "src_ip": data[key]['src_ip'],
                 "dest_ip": data[key]['dest_ip'],
                 "src_port": data[key]['src_port'],
                 "dst_port": data[key]['dst_port'],
                 "length": data[key]['length'],
                 "score": data[key]['prediction'][0],
                 "detection": data[key]['prediction'][1]}
            flows_dump.append(f)

        with open(self.csv_file_path, "a+") as output:
            csv_writer = csv.DictWriter(output, fieldnames=flows_dump[0].keys())
            if output.tell() == 0:
                # the file is just created, write headers
                csv_writer.writeheader()

            csv_writer.writerows(flows_dump)

    def get_row_style(self, prediction):
        styles = []
        if prediction[1] != "Normal":
            styles.append("bold")
            styles.append("bright_white")
            if prediction[0] >= self.at:
                styles.append("red")
            elif prediction[0] >= self.wt:
                styles.append("yellow")

        if styles:
            return f"[{' '.join(styles)}]"
        else:
            return ""

    def get_remarks(self, prediction):
        if prediction[1] != "Normal":
            if prediction[0] >= self.at:
                return "ALERT"
            elif prediction[0] >= self.wt:
                return "Warning"
        return ""

    def update_flows(self, data):
        latest = []
        self.last_time_updated = data["latest_timestamp"]
        for f in data["flows"]:
            name = f["name"]
            latest.append(name)
            f["prediction"][0] = float(f["prediction"][0])
            self.latest_n_flows.put(name, f)
        return latest

    def start(self):
        with Live(screen=False, auto_refresh=False, transient=False) as live:
            while True:
                is_early_okay, data = self.get_updates()

                if not is_early_okay:
                    self.closing()
                    break

                updated_flows = self.update_flows(data)
                # if updated_flows:
                #     self.recently_updated_flows = updated_flows

                if self.latest_n_flows:
                    table = Table(
                        "Flow ID", "Src IP", "Src Port", "Dst IP",
                        "Dst Port", "Length", "Prediction",
                        Column(header="Confidence", justify="right"), "Remarks", "Updated at",
                        title=f"Flows count: {len(self.latest_n_flows)}",
                    )

                    for k in self.latest_n_flows.ordered_keys:
                        f = self.latest_n_flows[k]
                        style = self.get_row_style(f['prediction'])
                        # print(f"[{remarks}]{f.name}")
                        table.add_row(
                            f"{style}{f['name']}",
                            f"{style}{f['src_ip']}",
                            f"{style}{f['src_port']}",
                            f"{style}{f['dest_ip']}",
                            f"{style}{f['dst_port']}",
                            f"{style}{f['length']}",
                            f"{style}{f['prediction'][1]}",
                            f"{style}{f['prediction'][0]}",
                            f"{style}{self.get_remarks(f['prediction'])}",
                            f"{style}{datetime.fromtimestamp(f['last_updated']).strftime(self.timestamp_format)}",
                        )
                    live.update(table, refresh=True)

                    if self.log_flows and data["flows"]:
                        self.write_csv_line(self.latest_n_flows)
                time.sleep(self.refresh_wait)
