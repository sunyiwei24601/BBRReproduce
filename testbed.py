from time import sleep
import sys
MININET_PATH = '/home/kyle/Desktop/mininet'
sys.path.append(MININET_PATH)
from mininet.net import Mininet
from mininet.clean import cleanup
from mininet.node import Node
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink, TCIntf
from util import iperf_cmd, genericCC_PATH, copa_sender_cmd, set_kernel_cc_algorithm
import time
import os
import _thread

# MININET_PATH = '/root/mininet'
LOG_PATH = 'logs/'


class MyTopo(Topo):
    def build(self, n=2, delay="10ms", loss=0, bw=10, jitter=None):
        """create topology by specified parameters

        Args:
            n (int, optional): nums of host pairs(n receiver and n sender). Defaults to 2.
            delay (str, optional): transmit delay (e.g. '1ms' ). Defaults to "10ms".
            loss (int, optional): loss (e.g. '1%' ). Defaults to 0.
            bw (int, optional): bandwidth in mb/s (e.g. 10 for '10m'). Defaults to 10mbps.
            jitter (_type_, optional): jitter (e.g. '1ms'). Defaults to None.
        """  
        senderHosts = [self.addHost(f'hs{x}') for x in range(1, n+1)]
        receiverHosts = [self.addHost(f'hr{x}') for x in range(1, n+1)]
        s1 = self.addSwitch('s1')
        n = 1
        for senderHost in senderHosts:
            #link configuration could refer to mininet.link.config function
            self.addLink(senderHost, s1, delay=delay, loss=loss, bw=bw, jitter=jitter)
            n+=1
        for recevierHost in receiverHosts:
            self.addLink(recevierHost, s1, delay=delay, loss=loss, bw=bw, jitter=jitter)

class CCTest():
    def __init__(self, clean_logs=False):
        self.clean_logs = clean_logs
        pass
    
    def test_single_cc(self, cctype="cubic", n=2, delay="10ms", loss=0, bw=10, jitter=None, duration=60):
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
        net = self.generate_network(n, bw, delay, loss, jitter)
        
        time_id = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        parameter_string = f"{cctype}_{n}hosts_delay={delay}_loss={loss}_bw={bw}_duration={duration}"
        print(f"current Test: single cc algorithm test paramets: {parameter_string}")
        logs_dirname = f"./{LOG_PATH}" + time_id + "_" + parameter_string

        os.makedirs(logs_dirname, exist_ok=True)
        
        s1 = net.getNodeByName('s1')
        s1.cmd(f'ethstats -t -n 1 -c {duration+5} > {logs_dirname}/ethstats.log  2>&1 &')
        
        # start a new interactive cmd to debug
        # _thread.start_new_thread(lambda:CLI(net), () )
        for i in range(1, n+1):
            senderHost, receiverHost = net.getNodeByName(f'hs{i}', f'hr{i}')
            if cctype in ["cubic", "bbr"]:
                self.run_kernel_test(senderHost, receiverHost, cctype, logs_dirname, duration)
            elif cctype == "copa":
                self.run_copa_test(senderHost, receiverHost, cctype, logs_dirname, duration)
            else:
                print("Unknown CC Algorithm: ", cctype)
                
        sleep(duration + 5 )
        net.stop()
        
        if self.clean_log:
            self.clean_log(logs_dirname)
    
    def test_multi_cc(self, cc1, cc2, cc1_host_n=1, cc2_host_n=1, delay="10ms", loss=0, bw=10, jitter=None, duration=60):
        """like test_single_cc, but use different cc algorithms on hosts
        Args:
            cc1 (_type_): first cc algorithm,  could be "cubic", "bbr", "copa", "reno", "bbrplus"
            cc2 (_type_): like cc2
            cc1_host_n (int, optional): number of hosts using first cc algorithm. Defaults to 1.
            cc2_host_n (int, optional): _description_. Defaults to 1.
            others: refer to test_single_cc parameters
        """
        net = self.generate_network(cc1_host_n + cc2_host_n, bw, delay, loss, jitter)
        
        time_id = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        parameter_string = f"{cc1}{cc1_host_n}_{cc2}{cc2_host_n}_delay={delay}_loss={loss}_bw={bw}_duration={duration}"
        print(f"current Test: single cc algorithm test paramets: {parameter_string}")
        logs_dirname = "./logs/" + time_id + "_" + parameter_string

        os.makedirs(logs_dirname, exist_ok=True)
        
        
        s1 = net.getNodeByName('s1')
        s1.cmd(f'ethstats -t -n 1 -c {duration+5} > {logs_dirname}/ethstats.log  2>&1 &')
        
        cctypes = [cc1] * cc1_host_n + [cc2] * cc2_host_n
        for _, cctype in enumerate(cctypes):
            i = _ + 1
            senderHost, receiverHost = net.getNodeByName(f'hs{i}', f'hr{i}')
            if cctype in ["cubic", "bbr", "bbrplus"]:
                self.run_kernel_test(senderHost, receiverHost, cctype, logs_dirname, duration)
            elif cctype == "copa":
                self.run_copa_test(senderHost, receiverHost, cctype, logs_dirname, duration)
            else:
                print("Unknown CC Algorithm: ", cctype)
                
        sleep(duration + 5 )
        net.stop()
        if self.clean_log:
            self.clean_log(logs_dirname)
            
    def generate_network(self, n, bw, delay, loss, jitter):
        """generate a network by given topology and return the network"""
        cleanup()
        topo = MyTopo(n=n, bw=bw, delay=delay, loss=loss, jitter=jitter)
        net = Mininet(topo=topo, waitConnected=False, link=TCLink) # link=TCLink is important to enable link limits
        print("links: ", topo.links())
        print("hosts: ", topo.hosts())
        net.start()
        return net

    def run_copa_test(self, senderHost, receiverHost, cctype, logs_dirname, duration):
        # for copa, use genericCC's sender/receiver scheme
        output_file = logs_dirname + f'/{senderHost.name}_copa.log'
        receiverHost.cmd(f'{genericCC_PATH}/receiver &')
        # print(f"{receiverHost.name} receiver init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

        senderHost.cmd(copa_sender_cmd(serverip=receiverHost.IP(), onduration=duration*1000, output_file=output_file))
        # print(f"{senderHost.name} sender init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

    def run_kernel_test(self, senderHost, receiverHost, cctype, logs_dirname, duration):
        # first set the tcp cc algorithm on host
        set_kernel_cc_algorithm(senderHost, cctype)
        
        # for cubic and bbr, use iperf scheme
        output_file = logs_dirname + f'/{senderHost.name}_iperf.log'
        receiverHost.cmd(iperf_cmd(side="server"))
        # print(f"{receiverHost.name} receiver init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

        senderHost.cmd(iperf_cmd(address=receiverHost.IP(), time=duration, output_file=output_file))
        # print(f"{senderHost.name} sender init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

    def clean_log(self, logs_dirname):
        if self.clean_logs:
            del_list = os.listdir(logs_dirname)
            for file in del_list:
                os.remove(os.path.join(logs_dirname, file))
            os.removedirs(logs_dirname)
        
if __name__ == '__main__':
    n = 3
    duration = 30
    delay = "3ms"
    bw = 10 #mbps
    loss = 3
    jitter = "200ms"
    
    # use this line to write log to trash dir, easier to clean logs
    LOG_PATH = "logs/trash/" 
    t = CCTest(clean_logs=False)
    
    t.test_single_cc("copa", n=1, delay='10ms', loss=3, bw=10, jitter=None, duration=10)
    # t.test_multi_cc("copa", "cubic", cc1_host_n=1, cc2_host_n=1, duration=10, bw=bw, delay=delay, loss=loss)

    