import os
from typing import Tuple
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import logging
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path

import tensorflow as tf
from tensorflow.python.framework.errors_impl import UnimplementedError
from tensorflow.keras.preprocessing.sequence import pad_sequences
from scapy.all import *


logger = logging.getLogger("earlytool-monitor")


class BaseClassifier(ABC):
    def __init__(self, *args, **kwargs):
        self.model = None
        self.max_header_size = 48
        self.max_payload_size = 400
        self.padding_position = "post"
        self.label_code = []
        self.can_use_gpu = len(tf.config.list_physical_devices('GPU')) > 0
        self.current_dir = Path(__file__).parent.resolve()

    def process_flow(self, packets):
        packets_header = []
        packets_payload = []

        for packet, _ in packets:
            # header = []
            payload = []
            if packet.haslayer(TCP):
                packet_type = TCP
            elif packet.haslayer(UDP):
                packet_type = UDP

            header = list(packet[packet_type].raw_packet_cache)[:self.max_header_size]
            if packet.haslayer(Raw):
                payload = list(bytes(packet[packet_type].payload))[:self.max_payload_size]

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
    def get_confidence(self, score) -> float:
        raise NotImplementedError("Must override get_confidence")

    @abstractmethod
    def get_label(self, score) -> str:
        return self.label_code[np.argmax(score)]

    def predict(self, flow_packets) -> Tuple[float, str]:
        processed_flow = self.process_flow(flow_packets)

        # Adding a batch dimension
        processed_flow = np.expand_dims(processed_flow, axis=0)

        if self.can_use_gpu:
            try:
                score = self.model.predict(processed_flow)
            except UnimplementedError:
                # if the gpu is being used for something else
                logger.warning("Cannot use GPU. Using CPU for predictions.")
                self.can_use_gpu = False
                with tf.device('/cpu:0'):
                    score = self.model.predict(processed_flow)
        else:
            with tf.device('/cpu:0'):
                score = self.model.predict(processed_flow)

        prediction = (self.get_confidence(score), self.get_label(score))
        return prediction