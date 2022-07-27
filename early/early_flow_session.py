# import csv
import sys
import time
import importlib.util
from pathlib import Path
from cicflowmeter.flow_session import FlowSession

from early.early_flow import EarlyFlow


class EarlyFlowSession(FlowSession):
    """Creates a list of network flows."""

    def __init__(self, *args, **kwargs):
        super(EarlyFlowSession, self).__init__(*args, **kwargs)
        self.last_flow_updated = None

        # self.classifier = Classifier("model_1dcnn_0604-134012_7.h5")
        self.classifier = self.load_classifer()

    def load_classifer(self):
        module_name = Path(self.classifier_module).name
        spec = importlib.util.spec_from_file_location(module_name, self.classifier_module)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module.EarlyClassifier()

    def on_packet_received(self, packet):
        result_tup = super(EarlyFlowSession, self).on_packet_received(packet)

        # If there is flow
        if result_tup:
            flow, flow_key = result_tup
            print(f"No. of packets analyzed: {self.packets_count}", end="\r")
            # print(f"Packets {self.packets_count}")

            flow.model_prediction = self.classifier.predict(flow.packets)
            # print(f"fin flag: {flow.get_data()['fin_flag_cnt']}")

            self.flow_deque.appendleft((flow_key, flow.to_dict()))
            # self.update_flow_display((packet_flow_key, count))
            time.sleep(self.sniffing_delay / 1000.0)

        return result_tup


def generate_session_class(output_mode, classifier_path, flow_deque, sniffing_delay):
    return type(
        "NewFlowSession",
        (EarlyFlowSession,),
        {
            "output_mode": output_mode,
            # "output_file": output_file,
            "flow_class": EarlyFlow,
            "classifier_module": classifier_path,
            "flow_deque": flow_deque,
            "sniffing_delay": sniffing_delay,
        },
    )