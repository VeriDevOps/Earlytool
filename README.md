# Earlytool

## Description
Repo for Early Tool

## Installation
It requires 3.8+ version of Python.

```sh
git clone https://gitlab.abo.fi/veridevops/earlytool
cd earlytool
python setup.py install
```

## Usage
It has two main components which should be executed in separate console windows.

### 1) Monitor
This component reads packets either from a PCAP file or a network interface. It constructs flows and get corresponding predictions from a given model. It runs a HTTP server which can be used to get fetch flows information.

```sh
Usage: early_monitor [OPTIONS]

Options:
  -i, --interface TEXT   Analyze live data from the network interface.
  -f, --pfile PATH       Analyze data from a PCAP file.
  -c, --classifier PATH  Path to a classifier python module that will be used
                         for making predictions. If the module exists in the
                         early/classifier folder, then just provide the name of
                         module without '.py', e.g., random_classifier
                         (default).
  -d, --delay-millisecond INTEGER
                         Add a delay of d milliseconds after sniffing a packet.
                         E.g., 0 (default) means no delay.
  --help                 Show this message and exit.

Constraints:
  {--interface, --pfile}  exactly 1 required
```

Read packets from a PCAP file:
```sh
early_monitor -f /home/user/earlytool/example_pcap/traffic_5f_ni.pcap
```

Or capture packets from a network interface: (**need root permission**)
```sh
sudo early_monitor -i eno1
```

### 2) Command Line Interface Display
This component fetches results from the monitor and displays flows in the command line.

```sh
Usage: early_display [OPTIONS]

Options:
  -u, --url-early TEXT      URL endpoint to get updates from Early tool. E.g.,
                            0.0.0.0:9400 (default)
  -w, --warning-threshold FLOAT RANGE
                            Warning threshold from 0 to 100. E.g., 40.0
                            (default)  [0<=x<=100]
  -a, --alert-threshold FLOAT RANGE
                            Alert threshold from 0 to 100. E.g., 40.0 (default)
                            [0<=x<=100]
  -r, --refresh-millisecond INTEGER
                            Refresh results after every r milliseconds. E.g.,
                            250 (default)
  -s, --show-flows INTEGER  Maximum number of flows to display.
  --help                    Show this message and exit.
```

## Example

1) Run the **display** to show 50 recently updated flows and update the results after every 500 milliseconds.

```sh
early_display -s 50 -r 500 -w 40 -a 50 
```

![monitor's output in the terminal](./doc_images/term_display.svg)


2) Run the **monitor** to read every packet from the given PCAP file with a delay of 1000 milliseconds and use a trained model to get predictions:
```sh
early_monitor -f example_pcap/traffic_5f_ni.pcap -c trained_classifier -d 1000
```

![monitor's output in the terminal](./doc_images/term_monitor.svg)
