# import csv
import sys
import time
import importlib.util
from pathlib import Path
from collections import defaultdict
from scapy.all import TCP
from scapy.sessions import DefaultSession

from features.context.packet_direction import PacketDirection
from features.context.packet_flow_key import get_packet_flow_key
from flow import Flow

EXPIRED_UPDATE = 120
MACHINE_LEARNING_API = "http://localhost:8000/predict"
GARBAGE_COLLECT_PACKETS = 100000


class FlowSession(DefaultSession):
    """Creates a list of network flows."""

    def __init__(self, *args, **kwargs):
        self.flows = {}
        self.flows_completed_by_FIN = set()
        self.csv_line = 0

        # if self.output_mode == "flow":
        #     output = open(self.output_file, "w")
        #     self.csv_writer = csv.writer(output)

        self.packets_count = 0

        self.last_flow_updated = None

        # self.classifier = Classifier("model_1dcnn_0604-134012_7.h5")
        self.classifier = self.load_classifer()

        self.clumped_flows_per_label = defaultdict(list)

        super(FlowSession, self).__init__(*args, **kwargs)

    def load_classifer(self):
        module_name = Path(self.classifier_module).name
        spec = importlib.util.spec_from_file_location(module_name, self.classifier_module)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module.EarlyClassifier()

    def toPacketList(self):
        # Sniffer finished all the packets it needed to sniff.
        # It is not a good place for this, we need to somehow define a finish signal for AsyncSniffer
        # self.garbage_collect(None)
        return super(FlowSession, self).toPacketList()

    def on_packet_received(self, packet):
        count = 0
        direction = PacketDirection.FORWARD

        if self.output_mode != "flow":
            if "TCP" not in packet:
                return
            elif "UDP" not in packet:
                return

        try:
            # Creates a key variable to check
            packet_flow_key = get_packet_flow_key(packet, direction)
            flow = self.flows.get((packet_flow_key, count))
        except Exception:
            return

        self.packets_count += 1
        print(f"No. of packets analyzed: {self.packets_count}", end="\r")
        # print(f"Packets {self.packets_count}")

        # If there is no forward flow with a count of 0
        if flow is None:
            # There might be one of it in reverse
            direction = PacketDirection.REVERSE
            packet_flow_key = get_packet_flow_key(packet, direction)
            flow = self.flows.get((packet_flow_key, count))

        if flow is None:
            # If no flow exists create a new flow
            # print("Hello non")
            direction = PacketDirection.FORWARD
            flow = Flow(packet, direction, len(self.flows))
            packet_flow_key = get_packet_flow_key(packet, direction)
            self.flows[(packet_flow_key, count)] = flow
        elif (packet.time - flow.latest_timestamp) > EXPIRED_UPDATE:
            # If the packet exists in the flow but the packet is sent
            # after too much of a delay than it is a part of a new flow.
            # print("Hello exp", len(flow.packets))
            expired = EXPIRED_UPDATE
            while (packet.time - flow.latest_timestamp) > expired:
                count += 1
                expired += EXPIRED_UPDATE
                flow = self.flows.get((packet_flow_key, count))

                if flow is None:
                    flow = Flow(packet, direction, len(self.flows))
                    self.flows[(packet_flow_key, count)] = flow
                    break
        elif (packet_flow_key, count) in self.flows_completed_by_FIN:
            # If the packets exists in the flow but the flow
            # has been completed by a FIN flag previously
            while True:
                count += 1
                flow = self.flows.get((packet_flow_key, count))

                if flow is None:
                    flow = Flow(packet, direction, len(self.flows))
                    self.flows[(packet_flow_key, count)] = flow
                    break

        if packet.haslayer(TCP) and "F" in str(packet[TCP].flags):
            # print("Hello f", packet[TCP].flags)
            # If it has FIN flag then early collect flow and continue
            # print("####### Received FIN")
            self.flows_completed_by_FIN.add((packet_flow_key, count))
            # self.garbage_collect(packet.time)

        flow.add_packet(packet, direction)
        # print("Hello out", len(flow.packets))
        # if not self.url_model:
        #     GARBAGE_COLLECT_PACKETS = 10000

        # if self.packets_count % GARBAGE_COLLECT_PACKETS == 0:
        #     print(f"####### Packet count: {self.packets_count}")
        #     self.garbage_collect(packet.time)

        flow.model_prediction = self.classifier.predict(flow.packets)
        # print(f"fin flag: {flow.get_data()['fin_flag_cnt']}")

        self.flow_deque.appendleft(((packet_flow_key, count), flow.to_dict()))
        # self.update_flow_display((packet_flow_key, count))
        time.sleep(self.sniffing_delay / 1000.0)

    def get_flows(self) -> list:
        return self.flows.values()

    def garbage_collect(self, latest_time) -> None:
        # TODO: Garbage Collection / Feature Extraction should have a separate thread
        if not self.url_model:
            print("Garbage Collection Began. Flows = {} ... ".format(len(self.flows)), end="")
        keys = list(self.flows.keys())
        for k in keys:
            flow = self.flows.get(k)

            if (
                latest_time is None
                or latest_time - flow.latest_timestamp > EXPIRED_UPDATE
                or flow.duration > 90
            ):
                data = flow.get_data()

                if self.csv_line == 0:
                    self.csv_writer.writerow(data.keys())

                self.csv_writer.writerow(data.values())
                self.csv_line += 1

                del self.flows[k]
        if not self.url_model:
            print("Garbage Collection Finished. Flows = {}".format(len(self.flows)))


def generate_session_class(output_mode, classifier_module, flow_deque, sniffing_delay):
    return type(
        "NewFlowSession",
        (FlowSession,),
        {
            "output_mode": output_mode,
            # "output_file": output_file,
            "classifier_module": classifier_module,
            "flow_deque": flow_deque,
            "sniffing_delay": sniffing_delay,
        },
    )
