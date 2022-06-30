import time
import requests
# from rich.console import Console
from utils import DequeDict
from rich.live import Live
from rich.table import Table, Column


class CLIDisplay:
    def __init__(self, early_host, wt, at, refresh_millisecond, max_nb_flow_display):
        self.early_host = early_host
        self.refresh_wait = refresh_millisecond / 1000.0
        self.wt = wt
        self.at = at
        self.last_time_updated = 0.0

        self.latest_n_flows = DequeDict(maxlen=max_nb_flow_display)
        self.recently_updated_flows = []
        self.just_started = True

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

    def get_updates(self):
        data = None
        is_early_okay = False
        msg_printed = False
        early_url = f"http://{self.early_host}/status?last_time={self.last_time_updated}"

        while True:
            try:
                r = requests.get(early_url)
                is_early_okay = True
                break
            except requests.exceptions.ConnectionError:
                if self.just_started:
                    if not msg_printed:
                        print(f"Waiting for Early tool to start at {self.early_host} ...")
                        msg_printed = True
                    time.sleep(1)
                else:
                    print(f"Early tool at {self.early_host} is stopped.")
                    break

        self.just_started = False
        if is_early_okay:
            if r.status_code != 200:
                print(f"Early tool's response status code is not 200. It is {r.status_code}.")
                is_early_okay = False
            else:
                data = r.json()

        return is_early_okay, data

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

    def closing(self):
        # print([d["name"] for d in self.latest_n_flows.values()])
        print("Exiting ...")