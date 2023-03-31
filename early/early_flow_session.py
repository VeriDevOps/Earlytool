import sys
import time
import logging
import importlib.util
from pathlib import Path

from cicflowmeter.features.context.packet_direction import PacketDirection
from cicflowmeter.features.context.packet_flow_key import get_packet_flow_key
from cicflowmeter.flow_session import FlowSession

from early.early_flow import EarlyFlow

logger = logging.getLogger("earlytool-monitor")


class EarlyFlowSession(FlowSession):
    """Creates a list of network flows."""

    def __init__(self, *args, **kwargs):
        super(EarlyFlowSession, self).__init__(*args, **kwargs)
        self.last_flow_updated = None
        self.__csv_file_path = None
        if self.per_packet:
            logger.info("Getting per packet predictions ...")

        self.classifier = self.load_classifier()

    def load_classifier(self):
        module_name = Path(self.classifier_module).name
        spec = importlib.util.spec_from_file_location(module_name, self.classifier_module)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module.EarlyClassifier()

    @property
    def csv_file_path(self):
        if self.__csv_file_path is None:
            # Defining the path of the CSV file
            self.__csv_file_path = self.output_directory / f"flows_{time.strftime('%m%d-%H%M%S')}.csv"

            logger.info(f"Dumping flows to {self.__csv_file_path}")
        return self.__csv_file_path

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

            if logger.isEnabledFor(logging.INFO):
                print(f"No. of packets analyzed: {self.packets_count}", end="\r")
            # print(f"Packets {self.packets_count}")

            flow.model_prediction = self.classifier.predict(flow.packets)
            # print(f"fin flag: {flow.get_data()['fin_flag_cnt']}")

            self.flow_deque.appendleft(flow.to_dict())

            time.sleep(self.sniffing_delay / 1000.0)

        return result_tup


def generate_session_class(output_mode, dump_incomplete_flows, nb_workers,
                           classifier_path, flow_deque, sniffing_delay, per_packet, flow_timeout):
    return type(
        "NewFlowSession",
        (EarlyFlowSession,),
        {
            "output_mode": output_mode,
            "dump_incomplete_flows": dump_incomplete_flows,
            "nb_workers": nb_workers,
            # "output_file": output_file,
            "flow_class": EarlyFlow,
            "classifier_module": classifier_path,
            "flow_deque": flow_deque,
            "sniffing_delay": sniffing_delay,
            "per_packet": per_packet,
            "dump_packet_indexes": True,
            "flow_timeout": flow_timeout,
        },
    )
