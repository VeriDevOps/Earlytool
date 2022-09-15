import sys
import time
import importlib.util
from pathlib import Path

from cicflowmeter.features.context.packet_direction import PacketDirection
from cicflowmeter.features.context.packet_flow_key import get_packet_flow_key
from cicflowmeter.flow_session import FlowSession

from early.early_flow import EarlyFlow


class EarlyFlowSession(FlowSession):
    """Creates a list of network flows."""

    def __init__(self, *args, **kwargs):
        super(EarlyFlowSession, self).__init__(*args, **kwargs)
        self.last_flow_updated = None

        if self.per_packet:
            print("Get per packet prediction")

        self.classifier = self.load_classifier()

    def load_classifier(self):
        module_name = Path(self.classifier_module).name
        spec = importlib.util.spec_from_file_location(module_name, self.classifier_module)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module.EarlyClassifier()

    def on_packet_received(self, packet):
        if self.per_packet:
            # If we are doing per packet prediction, then we will just create a new flow
            # whenever we receive a new packet

            self.packets_count += 1

            direction = PacketDirection.FORWARD
            flow = self.flow_class(packet, direction, self.packets_count)
            packet_flow_key = get_packet_flow_key(packet, direction)
            # self.flows[(packet_flow_key, 0)] = flow
            flow.add_packet(packet, direction)

            result_tup = (flow, (packet_flow_key, self.packets_count))
        else:
            result_tup = super(EarlyFlowSession, self).on_packet_received(packet)

        # If there is flow
        if result_tup:
            flow, _ = result_tup
            print(f"No. of packets analyzed: {self.packets_count}", end="\r")
            # print(f"Packets {self.packets_count}")

            flow.model_prediction = self.classifier.predict(flow.packets)
            # print(f"fin flag: {flow.get_data()['fin_flag_cnt']}")

            self.flow_deque.appendleft(flow.to_dict())

            time.sleep(self.sniffing_delay / 1000.0)

        return result_tup


def generate_session_class(output_mode, classifier_path, flow_deque, sniffing_delay, per_packet):
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
            "per_packet": per_packet,
        },
    )