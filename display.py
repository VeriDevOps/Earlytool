import cloup

from early.display import __version__
from early.display.cli_display import Display


@cloup.command()
@cloup.option("-u", "--url-early", type=str, default="0.0.0.0:9400", show_default=True,
              help="URL endpoint to get updates from Early tool.")
@cloup.option("-w", "--warning-threshold", type=cloup.FloatRange(min=0, max=100), default=40.0, show_default=True,
              help="Warning threshold from 0 to 100 w.r.t. the confidence score.")
@cloup.option("-a", "--alert-threshold", type=cloup.FloatRange(min=0, max=100), default=50.0, show_default=True,
              help="Alert threshold from 0 to 100 w.r.t. the confidence score.")
@cloup.option("-r", "--refresh-millisecond", type=int, default=250, show_default=True,
              help="Refresh results after every r milliseconds.")
@cloup.option("-f", "--timestamp-format", type=str, default="%y-%m-%d %H:%M:%S", show_default=True,
              help="Format the timestamp in the Updated at column.")
@cloup.option("-s", "--show-flows", type=int, default=100, show_default=True,
              help="Maximum number of flows to display.")
@cloup.option("-l", "--write-log", is_flag=True,
              help="Dump flows to a log file.")
@cloup.version_option(version=__version__)
def main(url_early, warning_threshold, alert_threshold, refresh_millisecond, timestamp_format, show_flows, write_log):
    display = Display(
        url_early,
        warning_threshold,
        alert_threshold,
        refresh_millisecond,
        timestamp_format,
        show_flows,
        write_log
    )

    try:
        display.start()
    except KeyboardInterrupt:
        print("Exiting ...")


if __name__ == "__main__":
    main()