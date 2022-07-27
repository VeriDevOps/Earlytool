import time
# from rich.console import Console
from rich.live import Live
from rich.table import Table, Column

from early.display.base import BaseDisplay


class Display(BaseDisplay):
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
        for k, d in data["flows"]:
            tuple_k = (tuple(k[0]), k[1])
            latest.append(d["name"])
            d["prediction"][0] = float(d["prediction"][0])
            self.latest_n_flows.put(tuple_k, d)
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
                        "Flow ID", "Source IP", "Destination IP", "Length", "Prediction",
                        Column(header="Confidence", justify="right"), "Remarks",
                        title=f"Flows count: {len(self.latest_n_flows)}",
                    )

                    for k in reversed(self.latest_n_flows.data):
                        f = self.latest_n_flows[k]
                        style = self.get_row_style(f['prediction'])
                        # print(f"[{remarks}]{f.name}")
                        table.add_row(
                            f"{style}{f['name']}",
                            f"{style}{f['src_ip']}",
                            f"{style}{f['dest_ip']}",
                            f"{style}{f['length']}",
                            f"{style}{f['prediction'][1]}",
                            f"{style}{f['prediction'][0]}",
                            f"{style}{self.get_remarks(f['prediction'])}",
                        )
                    live.update(table, refresh=True)
                time.sleep(self.refresh_wait)