import argparse

from cli_display import CLIDisplay


def main(args):
    display = CLIDisplay(
        args.url_early,
        args.warning_threshold,
        args.alert_threshold,
        args.refresh_millisecond,
        args.show_flows,
    )

    try:
        display.start()
    except KeyboardInterrupt:
        print("Exiting ...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        "--url",
        action="store",
        dest="url_early",
        default="0.0.0.0:9400",
        help="URL endpoint to get updates from Early tool. e.g 0.0.0.0:9400 (default)",
    )

    parser.add_argument(
        "-s"
        "--show_flows",
        action="store",
        dest="show_flows",
        default=100,
        type=int,
        help="Maximum number of flows to display.",
    )

    parser.add_argument(
        "-w",
        action="store",
        dest="warning_threshold",
        default=40.0,
        type=float,
        help="Warning threshold. E.g., 40.0 (default)",
    )

    parser.add_argument(
        "-a",
        action="store",
        dest="alert_threshold",
        default=60.0,
        type=float,
        help="Alert threshold. E.g., 60.0 (default)",
    )

    parser.add_argument(
        "-r",
        action="store",
        dest="refresh_millisecond",
        default=250,
        type=int,
        help="Refresh results after every r milliseconds. E.g., 250 (default)",
    )

    # parser.add_argument(
    #     "--output",
    #     default=f"output_{time.strftime('%d%m-%H%M%S')}.csv",
    #     help="output file name (in flow mode) or directory (in sequence mode)",
    # )

    args = parser.parse_args()

    main(args)
