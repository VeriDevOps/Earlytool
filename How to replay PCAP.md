# How to replay a PCAP file

## 1) Create a dummy network interface 

We will create and use a dummy network interface for replaying the network traffic. This way, we will more control over the traffic that we are replaying, and we will not disturb the other services utilizing the real network interfaces.

```shell
# 0. Ensure the "dummy" Linux kernel module is installed.
sudo lsmod | grep dummy
# 1. Install the "dummy" Linux kernel module if you don't see 
# any output (like: dummy    16384  0) from the previous command
sudo modprobe dummy
# 2. Ensure the "dummy" Linux kernel module is installed.
sudo lsmod | grep dummy
# 3. Create a virtual (dummy) interface named `eth10`.
sudo ip link add eth10 type dummy
# 4. Change this new interface's IP address to whatever you like
# (10.0.0.1 in this case).
sudo ip address change dev eth10 10.0.0.1
# 5. See the newly-created device and the IP address you just
# assigned to it.
ip address
```

If the interface is down, you can bring interface up or down using the ip command

```shell
ip link set dev eth10 up
```

And if you ever need to delete this device:
```shell
# 1. Delete this `eth10` dummy device you created.
sudo ip link delete eth10 type dummy
# 2. Ensure 'eth10' is deleted and doesn't show up here now.
ip address
```

More information here: 
1. https://unix.stackexchange.com/q/152331
2. https://www.xmodulo.com/how-to-assign-multiple-ip-addresses-to-one-network-interface-on-centos.html


## 2) Remove _Cooked linux_ layer from packets

Sometimes, in the recorded PCAP file, the packets have the _cooked linux_ layer as the last layer, as opposed to the _Ethernet_ layer. For example, in the below packet: 

```
###[ cooked linux ]### 
  pkttype   = unicast
  lladdrtype= 0x304
  lladdrlen = 6
  src       = ''
  proto     = IPv4
###[ IP ]### 
     version   = 4
     ihl       = 5
     tos       = 0x0
     len       = 60
     id        = 11912
     flags     = DF
     frag      = 0
     ttl       = 64
     proto     = tcp
     chksum    = 0xdc9b
     src       = 192.168.0.151
     dst       = 10.16.100.73
     \options   \
###[ TCP ]### 
        sport     = 39937
        dport     = 1883
        seq       = 3739984307
        ack       = 0
        dataofs   = 10
        reserved  = 0
        flags     = S
        window    = 65495
        chksum    = 0x2fc7
        urgptr    = 0
        options   = [('MSS', 65495), ('SAckOK', b''), ('Timestamp', (4118463279, 0)), ('NOP', None), ('WScale', 7)]
```

We need to fix that by replacing the _cooked linux_ layer with the Ethernet layer before we can replay the PCAP file. We use the `tcprewrite` to fix the issue. We need to overwrite the output format to Ethernet II, and supply the source MAC and dest MAC which the Cooked Capture format.

```shell
tcprewrite --dlt=enet --enet-dmac=52:54:00:11:11:11 --enet-smac=52:54:00:22:22:22 -i in.pcap -o out.pcap
```

`tcprewrite` appears to understand the concept of a two-way conversation, so comma-separated MACs can be specified for each participant in a two-way conversation.

More information:
1. https://osqa-ask.wireshark.org/questions/21562/editcap-from-linux-cooked-capture-to-ethernet-packet/
2. https://stackoverflow.com/questions/27831427/scapys-exported-linux-cooked-mode-capture-doesnt-open-in-wireshark

## 3) Replay the PCAP

We use the `tcpreplay` to the replay the traffic from the PCAP file over the dummy network interface we created.

```shell
sudo tcpreplay -v -i eth10 out.pcap
```
