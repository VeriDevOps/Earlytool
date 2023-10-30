from cicflowmeter.flow import Flow
from cicflowmeter.features.packet_count import PacketCount
from cicflowmeter.features.packet_time import PacketTime


class EarlyFlow(Flow):
    """This class summarizes the values of the features of the network flows"""

    def __init__(self, *args, **kwargs):
        super(EarlyFlow, self).__init__(*args, **kwargs)
        self.model_prediction = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "dest_ip": self.dest_ip,
            "src_ip": self.src_ip,
            "src_port": self.src_port,
            "dst_port": self.dest_port,
            "last_updated": float(self.packets[-1][0].time),
            "length": len(self.packets),
            "prediction": self.model_prediction,
        }

    def get_data(self, flow_id="") -> dict:
        """This method obtains the values of the features extracted from each flow.
        Returns:
           list: returns a List of values to be outputted into a csv file.
        """
        packet_count = PacketCount(self)
        packet_time = PacketTime(self)

        data = {
            "flow_id": flow_id,
            # Basic IP information
            "src_ip": self.src_ip,
            "dst_ip": self.dest_ip,
            "src_port": self.src_port,
            "dst_port": self.dest_port,
            "protocol": self.protocol,
            # Basic information from packet times
            "timestamp": packet_time.get_time_stamp(),
            "flow_duration": 1e3 * packet_time.get_duration(),  # in milliseconds
            # Count total packets
            "noofpackets": packet_count.get_total(),
            # Model's prediction for the flow
            "prediction_score": self.model_prediction[0],
            "prediction_label": self.model_prediction[1]
        }
        return data
