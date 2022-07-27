import os
import sys
from pathlib import Path
from scapy.sendrecv import AsyncSniffer

from early.early_flow_session import generate_session_class


def get_classifier_path(classifier_path):
    file = Path(classifier_path)

    # If the absolute path is given
    if file.exists():
        return classifier_path
    # If only the name is given
    else:
        current_folder = Path(__file__).resolve().parent
        file = current_folder / "classifier" / f"{classifier_path}.py"
        if file.exists():
            return str(file)
    return None


def create_sniffer(
        input_file, input_interface, output_mode, classifier_module, flow_deque, sniffing_delay,
):
    assert (input_file is None) ^ (input_interface is None)

    classifier_path = get_classifier_path(classifier_module)
    if not os.path.exists(classifier_path):
        print(f"=== Error: classifier module does not exist: {classifier_path}")
        sys.exit()

    print(f"Using classifier module: {classifier_path}")

    NewFlowSession = generate_session_class(
        output_mode, classifier_path, flow_deque, sniffing_delay)()

    if input_file is not None:
        if not os.path.exists(input_file):
            print(f"=== Error: PCAP file does not exist: {input_file}")
            sys.exit()

        return AsyncSniffer(
            offline=input_file,
            # filter="ip and (tcp or udp)",
            prn=None,
            session=NewFlowSession,
            store=False,
        )
    else:
        return AsyncSniffer(
            iface=input_interface,
            # filter="ip and (tcp or udp)",
            filter="ip and tcp",
            prn=None,
            session=NewFlowSession,
            store=False,
        )
