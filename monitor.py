import cloup
import logging
from cloup.constraints import If, IsSet, require_one
from collections import deque

from early import __version__
from early.broadcast_server import BroadcastServer
from early.sniffer import create_sniffer

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger("earlytool-monitor")

# Setting the logging level of the cicflowmeter lib to Warning, so we don't get any printouts from the lib
cic_logger = logging.getLogger("cicflowmeter")
cic_logger.setLevel(logging.WARNING)


@cloup.command(show_constraints=True)
@cloup.constraints.require_one(
    cloup.option("-i", "--interface", type=str, help="Analyze live data from the network interface.", multiple=False),
    cloup.option("-f", "--pfile", help="Analyze data from a PCAP file.",
                 type=cloup.Path(dir_okay=False, exists=True, readable=True), multiple=False)
)
@cloup.option("-b", "--bpf-filter", "bpf_filter", type=str, help="Filter network traffic using BPFs.",
              default="ip and (tcp or udp)", show_default=True)
@cloup.option("-c", "--classifier", default="random_classifier", show_default=True,
              help="Path to a classifier python module that will be used for making predictions. "
                   "If the module exists in the early/classifier folder, "
                   "then just provide the name of module without '.py'.",
              type=cloup.Path(dir_okay=False, readable=True), multiple=False)
@cloup.option("-o", "--output-csv", is_flag=True, help="output completed flows as csv", flag_value="csv")
@cloup.option("--in", "dump_incomplete_flows", is_flag=True,
              help="Dump incomplete flows to the csv file before existing the program.")
# @cloup.option("--dir", "output_directory", help="output directory (in csv mode). [default: current directory]",
#               default=str(Path.cwd()), type=cloup.Path(file_okay=False, exists=True, writable=True), multiple=False)
@cloup.option("-w", "--workers", type=int, default=2, multiple=False, show_default=True,
              help="No. of workers are used to write flows to a CSV file.")
@cloup.option("-t", "--flow-timeout", "flow_timeout", type=float, default=120.0, multiple=False, show_default=True,
              help="Specify the maximum duration in seconds as the flow timeout.")
@cloup.option("-d", "--delay-millisecond", type=int, default=0, multiple=False, show_default=True,
              help="Add a delay of d milliseconds after sniffing every packet.")
@cloup.option("-k", "--keep-flows", type=int, default=None,
              help="Maximum number of most recent flows to keep in memory. [default: unlimited]")
@cloup.option("-p", "--packets-per-detection", type=int, default=None,
              help="Maximum number of packets in a flow used for detection. [default: unlimited]")
@cloup.option("-r", "--per-packet", is_flag=True,
              help="Get a prediction per packet instead of per flow.")
@cloup.constraint(If(IsSet('dump_incomplete_flows'), then=require_one.hidden()), ['output_csv', ])
@cloup.version_option(version=__version__)
def main(
        interface, pfile, bpf_filter, classifier, output_csv, dump_incomplete_flows, workers, flow_timeout,
        delay_millisecond, keep_flows, packets_per_detection, per_packet
):
    flow_deque = deque(maxlen=keep_flows)

    sniffer = create_sniffer(
        pfile,
        interface,
        output_mode=output_csv,
        dump_incomplete_flows=dump_incomplete_flows,
        nb_workers=workers,
        # output_file=output,
        bpf_filter=bpf_filter,
        classifier_module=classifier,
        flow_deque=flow_deque,
        sniffing_delay=delay_millisecond,
        per_packet=per_packet,
        flow_timeout=flow_timeout,
        packets_per_detection=packets_per_detection,
    )

    webserver = BroadcastServer(queue=flow_deque, port=9400)

    try:
        webserver.startServer()
        sniffer.start()
        stopped = False

        sniffer.join()
        stopped = True
        input("\nPress enter to exit.")
    except KeyboardInterrupt:
        logger.info("Exiting...")
        if not stopped:
            sniffer.stop()
    except OSError as err:
        logger.error(str(err))
    finally:
        sniffer.join()
        webserver.stopServer()


if __name__ == "__main__":
    main()
