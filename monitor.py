import cloup
from collections import deque

from early.broadcast_server import BroadcastServer
from early.sniffer import create_sniffer


@cloup.command(show_constraints=True)
@cloup.constraints.require_one(
    cloup.option("-i", "--interface", type=str, help="Analyze live data from the network interface.", multiple=False),
    cloup.option("-f", "--pfile", help="Analyze data from a PCAP file.",
                 type=cloup.Path(file_okay=True, readable=True), multiple=False)
)
@cloup.option("-c", "--classifier", default="random_classifier",
              help="Path to a classifier python module that will be used for making predictions. "
                   "If the module exists in the early/classifier folder, "
                   "then just provide the name of module without '.py', e.g., random_classifier (default).",
              type=cloup.Path(file_okay=True, readable=True), multiple=False)
@cloup.option("-d", "--delay-millisecond", type=int, default=0, multiple=False,
              help="Add a delay of d milliseconds after sniffing a packet. E.g., 0 (default) means no delay.")
def main(interface, pfile, classifier, delay_millisecond):
    flow_deque = deque(maxlen=100)

    sniffer = create_sniffer(
        pfile,
        interface,
        output_mode="flow",
        # output_file=output,
        classifier_module=classifier,
        flow_deque=flow_deque,
        sniffing_delay=delay_millisecond,
    )

    webserver = BroadcastServer(queue=flow_deque, port=9400)
    webserver.startServer()
    sniffer.start()
    stopped = False

    try:
        sniffer.join()
        stopped = True
        input("\nPress enter to exit.")
    except KeyboardInterrupt:
        print("\nExiting...")
        if not stopped:
            sniffer.stop()
    finally:
        sniffer.join()
        webserver.stopServer()


if __name__ == "__main__":
    main()
