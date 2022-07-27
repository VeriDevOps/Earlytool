import cloup

from early.display.cli_display import Display


@cloup.command()
@cloup.option("-u", "--url-early", type=str, default="0.0.0.0:9400",
              help="URL endpoint to get updates from Early tool. E.g., 0.0.0.0:9400 (default)")
@cloup.option("-w", "--warning-threshold", type=cloup.FloatRange(min=0, max=100), default=40.0,
              help="Warning threshold from 0 to 100. E.g., 40.0 (default)")
@cloup.option("-a", "--alert-threshold", type=cloup.FloatRange(min=0, max=100), default=40.0,
              help="Alert threshold from 0 to 100. E.g., 40.0 (default)")
@cloup.option("-r", "--refresh-millisecond", type=int, default=250,
              help="Refresh results after every r milliseconds. E.g., 250 (default)")
@cloup.option("-s", "--show-flows", type=int, default=100,
              help="Maximum number of flows to display.")
def main(url_early, warning_threshold, alert_threshold, refresh_millisecond, show_flows):
    display = Display(
        url_early,
        warning_threshold,
        alert_threshold,
        refresh_millisecond,
        show_flows,
    )

    try:
        display.start()
    except KeyboardInterrupt:
        print("Exiting ...")


if __name__ == "__main__":
    main()
