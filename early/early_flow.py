from enum import Enum
from typing import Any

from cicflowmeter.flow import Flow


class EarlyFlow(Flow):
    """This class summarizes the values of the features of the network flows"""

    def __init__(self, packet: Any, direction: Enum, fid=0):
        super(EarlyFlow, self).__init__(packet, direction, fid)
        self.model_prediction = None

    def to_dict(self):
        return {
            "name": self.name,
            "dest_ip": self.dest_ip,
            "src_ip": self.src_ip,
            "length": len(self.packets),
            "prediction": self.model_prediction,
        }