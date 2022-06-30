import os
import sys
import argparse
# from rich.console import Console
# import cherrypy
# from collections import deque
# from rich.live import Live
from scapy.all import *
# from cherrypy.process.plugins import Daemonizer
from scapy.sendrecv import AsyncSniffer

from broadcast_server import BroadcastServer
from flow_session import generate_session_class


def create_sniffer(
        input_file, input_interface, output_mode, classifier_module, flow_deque, sniffing_delay,
):
    assert (input_file is None) ^ (input_interface is None)

    if not os.path.exists(classifier_module):
        print(f"=== Error: classifier module does not exist: {classifier_module}")
        sys.exit()

    print(f"Using classifier module: {classifier_module}")

    NewFlowSession = generate_session_class(
        output_mode, classifier_module, flow_deque, sniffing_delay)()

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


def main(args):
    flow_deque = deque(maxlen=100)

    sniffer = create_sniffer(
        args.input_file,
        args.input_interface,
        output_mode="flow",
        # output_file=args.output,
        classifier_module=args.classifier_module,
        flow_deque=flow_deque,
        sniffing_delay=args.delay_millisecond,
    )

    webserver = BroadcastServer(queue=flow_deque, port=9400)
    webserver.startServer()
    sniffer.start()
    stopped = False

    try:
        # print("Here before")
        sniffer.join()
        stopped = True
        input("\nPress enter to exit.")
        # print("Here after")
    except KeyboardInterrupt:
        print("\nExiting...")
        if not stopped:
            sniffer.stop()
    finally:
        sniffer.join()
        webserver.stopServer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-i",
        "--interface",
        action="store",
        dest="input_interface",
        help="capture online data from INPUT_INTERFACE",
    )

    input_group.add_argument(
        "-f",
        "--file",
        action="store",
        dest="input_file",
        help="capture offline data from INPUT_FILE",
    )

    # output_group = parser.add_mutually_exclusive_group(required=False)
    # output_group.add_argument(
    #     "-c",
    #     "--csv",
    #     "--flow",
    #     action="store_const",
    #     const="flow",
    #     dest="output_mode",
    #     help="output flows as csv",
    # )

    # url_model = parser.add_mutually_exclusive_group(required=False)
    # url_model.add_argument(
    #     "-u",
    #     "--url",
    #     action="store",
    #     dest="url_model",
    #     help="URL endpoint for send to Machine Learning Model. e.g http://0.0.0.0:80/prediction",
    # )

    parser.add_argument(
        "-c"
        "--classifier",
        action="store",
        dest="classifier_module",
        default="classifier/random_classifier.py",
        help="Classifier module used for making predictions. Default: classifier/random_classifier.py",
    )

    # parser.add_argument(
    #     "-r"
    #     "--read_packets",
    #     action="store",
    #     dest="max_nb_packets_read",
    #     default=0,
    #     type=int,
    #     help="Maximum number of packets to read from a file. Default: unlimited.",
    # )

    parser.add_argument(
        "-d",
        action="store",
        dest="delay_millisecond",
        default=0,
        type=int,
        help="Add a delay of d milliseconds after sniffing a packet. E.g., 0 (default: no delay)",
    )

    # parser.add_argument(
    #     "--wt",
    #     action="store",
    #     dest="warning_threshold",
    #     default=0.4,
    #     type=float,
    #     help="Warnig threshold",
    # )
    #
    # parser.add_argument(
    #     "--at",
    #     action="store",
    #     dest="alert_threshold",
    #     default=0.48,
    #     type=float,
    #     help="Alert threshold",
    # )

    # parser.add_argument(
    #     "--output",
    #     default=f"output_{time.strftime('%d%m-%H%M%S')}.csv",
    #     help="output file name (in flow mode) or directory (in sequence mode)",
    # )

    args = parser.parse_args()

    main(args)
