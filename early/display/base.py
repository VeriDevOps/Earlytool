import time
import requests

from early.utils import DequeDict


class BaseDisplay:
    def __init__(self, early_host, wt, at, refresh_millisecond, max_nb_flow_display):
        self.early_host = early_host
        self.refresh_wait = refresh_millisecond / 1000.0
        self.wt = wt
        self.at = at
        self.last_time_updated = 0.0

        self.latest_n_flows = DequeDict(maxlen=max_nb_flow_display)
        self.recently_updated_flows = []
        self.just_started = True

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

    def start(self):
        raise NotImplemented("Display must implement this method")

    def closing(self):
        # print([d["name"] for d in self.latest_n_flows.values()])
        print("Exiting ...")