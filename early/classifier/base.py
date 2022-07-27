import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path
from scapy.all import *
from keras.preprocessing.sequence import pad_sequences


class BaseClassifier(ABC):
    def __init__(self, *args, **kwargs):
        self.model = None
        self.max_header_size = 48
        self.max_payload_size = 400
        self.padding_position = "post"
        self.label_code = []
        self.current_dir = Path(__file__).parent.resolve()

    def process_flow(self, packets):
        # hp = pad_sequences(
        #     [list(p[0][TCP].raw_packet_cache) for p in packets], maxlen=self.max_header_size,
        #     dtype='float16', padding=self.padding_position,
        #     truncating=self.padding_position, value=0.0
        # )
        #
        # packets_payload = []
        # for p, _ in packets:
        #     if p.haslayer(Raw):
        #         payload = list(bytes(p[TCP].payload))
        #     else:
        #         payload = []
        #     packets_payload.append(payload)

        packets_header = []
        packets_payload = []

        for packet, _ in packets:
            header = []
            payload = []
            if packet.haslayer(TCP):
                header = list(packet[TCP].raw_packet_cache)[:self.max_header_size]
                if packet.haslayer(Raw):
                    payload = list(bytes(packet[TCP].payload))[:self.max_payload_size]
            elif packet.haslayer(UDP):
                header = list(packet[UDP].raw_packet_cache)[:self.max_header_size]
                if packet.haslayer(Raw):
                    payload = list(bytes(packet[UDP].payload))[:self.max_payload_size]
            packets_header.append(header)
            packets_payload.append(payload)

        hp = pad_sequences(
            packets_header, maxlen=self.max_header_size, dtype='float16', padding=self.padding_position,
            truncating=self.padding_position, value=0.0
        )

        pp = pad_sequences(
            packets_payload, maxlen=self.max_payload_size, dtype='float16', padding=self.padding_position,
            truncating=self.padding_position, value=0.0
        )

        x = np.concatenate((hp, pp), axis=1) / 255.0
        return x

    @abstractmethod
    def get_confidence(self, score):
        raise NotImplementedError("Must override get_confidence")

    @abstractmethod
    def get_label(self, score):
        return self.label_code[np.argmax(score)]

    def predict(self, flow_packets):
        processed_flow = self.process_flow(flow_packets)

        # Adding a batch dimension
        processed_flow = np.expand_dims(processed_flow, axis=0)

        score = self.model.predict(processed_flow)
        prediction = (self.get_confidence(score), self.get_label(score))
        return prediction