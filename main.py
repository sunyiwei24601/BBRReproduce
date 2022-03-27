from time import sleep
import sys
MININET_PATH = '/home/sunyiwei24601/Desktop/mininet'
sys.path.append(MININET_PATH)
from mininet.net import Mininet
from mininet.clean import cleanup
from mininet.node import Node
from mininet.topo import Topo
from mininet.link import TCLink
from util import iperf_cmd, genericCC_PATH, copa_sender_cmd, set_kernel_cc_algorithm
import time
import os
# MININET_PATH = '/root/mininet'
LOG_PATH = ''

class MyTopo(Topo):
    def build(self, n=2, delay="10ms", loss=0, bw=10, jitter=None):
        """create topology by specified parameters

        Args:
            n (int, optional): nums of host pairs(n receiver and n sender). Defaults to 2.
            delay (str, optional): transmit delay (e.g. '1ms' ). Defaults to "10ms".
            loss (int, optional): jitter (e.g. '1ms'). Defaults to 0.
            bw (_type_, optional): bandwidth in mb/s (e.g. '10m'). Defaults to 10mbps.
            jitter (_type_, optional): loss (e.g. '1%' ). Defaults to None.
        """
        senderHosts = [self.addHost(f'hs{x}') for x in range(1, n+1)]
        receiverHosts = [self.addHost(f'hr{x}') for x in range(1, n+1)]
        s1 = self.addSwitch('s1')

        for senderHost in senderHosts:
            #link configuration could refer to mininet.link.config function
            self.addLink(senderHost, s1, delay=delay, loss=loss, bw=bw, jitter=jitter)
        for recevierHost in receiverHosts:
            self.addLink(recevierHost, s1, delay=delay, loss=loss, bw=bw, jitter=jitter)

topos = { 'mytopo': ( lambda: MyTopo() ) }

def test_single_cc(cctype="cubic", n=2, delay="10ms", loss=0, bw=10, jitter=None, duration=60):
    """create topology based on parameter, running iperf test between pairs, write the throughput records into files 

    Args:
        cctype(str): the algorithm used in test, options: "cubic", "bbr", "copa", "reno"
        n (int, optional): _description_. Defaults to 2.
        delay (str, optional): _description_. Defaults to "10ms".
        loss (int, optional): _description_. Defaults to 0.
        bw (_type_, optional): _description_. Defaults to None.
        jitter (_type_, optional): _description_. Defaults to None.
        duration(int): the last time for the test. Defaults to 60 seconds.
    """
    cleanup()
    topo = MyTopo(n=n, bw=bw, delay=delay, loss=loss, jitter=jitter)
    net = Mininet(topo=topo, waitConnected=False, link=TCLink) # link=TCLink is important to enable link limits
    print("links: ", topo.links())
    print("hosts: ", topo.hosts())
    net.start()
    
    time_id = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
    parameter_string = f"{cctype}_{n}hosts_dealy={delay}_loss={loss}_bw={bw}_duration={duration}"
    print(f"current Test: single cc algorithm test paramets: {parameter_string}")
    logs_dirname = "./logs/" + time_id + "_" + parameter_string

    os.makedirs(logs_dirname, exist_ok=True)
    
    
    s1 = net.getNodeByName('s1')
    s1.cmd(f'ethstats -t -n 1 -c {duration+5} > {logs_dirname}/ethstats.log  2>&1 &')
    
    for i in range(1, n+1):
        senderHost, receiverHost = net.getNodeByName(f'hs{i}', f'hr{i}')
        if cctype in ["cubic", "bbr"]:
            # first set the tcp cc algorithm on host
            set_kernel_cc_algorithm(senderHost, cctype)
            
            # for cubic and bbr, use iperf scheme
            output_file = logs_dirname + f'/sender{i}_iperf.log'
            receiverHost.cmd(iperf_cmd(side="server"))
            senderHost.cmd(iperf_cmd(address=receiverHost.IP(), time=duration, output_file=output_file))
        elif cctype == "copa":
            # for copa, use genericCC's sender/receiver scheme
            output_file = logs_dirname + f'/sender{i}_copa.log'
            receiverHost.cmd(f'{genericCC_PATH}/receiver &')
            senderHost.cmd(copa_sender_cmd(serverip=receiverHost.IP(), onduration=duration*1000, output_file=output_file))
        else:
            print("Unknown CC Algorithm: ", cctype)
            
    sleep(duration + 20 )
    net.stop()


if __name__ == '__main__':
    n = 3
    duration = 30
    delay = "10ms"
    bw = 10 #mbps
    loss = 3
    test_single_cc("cubic", n=n, duration=30, bw=bw, delay=delay, loss=loss)
    test_single_cc("bbr", n=n, duration=30, bw=bw, delay=delay, loss=loss)
    test_single_cc("copa", n=n, duration=30, bw=bw, delay=delay, loss=loss)

    