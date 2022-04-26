from time import sleep
import sys
MININET_PATH = '/home/kyle/Desktop/mininet'
sys.path.append(MININET_PATH)
sys.path.append('~/mininet')
from mininet.net import Mininet
from mininet.clean import cleanup
from mininet.node import Node
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink, TCIntf
from util import iperf_cmd, genericCC_PATH, copa_sender_cmd, set_kernel_cc_algorithm, print_t
import time
import os
import _thread
import platform

# MININET_PATH = '/root/mininet'
LOG_PATH = 'logs/'
KERNEL_VERSION = platform.uname().release
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
        s2 = self.addSwitch('s2')
        
        # split delay into 2 links
        delay = int(delay[:-2])/2
        dealy = f"{delay}ms"
        
        self.addLink(s1, s2, delay="1ms", loss=loss, bw=bw, jitter=jitter)
        for senderHost in senderHosts:
            #link configuration could refer to mininet.link.config function
            self.addLink(senderHost, s1, delay=delay, loss=0, bw=bw, jitter=jitter)
        for recevierHost in receiverHosts:
            self.addLink(recevierHost, s2, delay=delay, loss=0, bw=bw, jitter=jitter)

class CCTest():
    def __init__(self, clean_logs=False, monitor_type="both", DEBUG=False):
        """
        Args:
            clean_logs (bool, optional): _description_. Defaults to False.
            monitor_type (str, optional): The monitor tool to use, 'ifstat' use to record by 100 microsecond
            'ethstats' use to record by second. Defaults to "both".
        """
        self.monitor_type = monitor_type
        self.clean_logs = clean_logs
        self.DEBUG = DEBUG
        pass
    
    def test_single_cc(self, cctype="cubic", n=2, delay="10ms", loss=0, bw=10, jitter=None, duration=60, start_delay=0):
        """create topology based on parameter, running iperf test between pairs, write the throughput records into files 
        Args:
            cctype(str): the algorithm used in test, options: "cubic", "bbr", "copa", "reno"
            n (int, optional): _description_. Defaults to 2.
            delay (str, optional): _description_. Defaults to "10ms".
            loss (int, optional): _description_. Defaults to 0.
            bw (_type_, optional): _description_. Defaults to None.
            jitter (_type_, optional): _description_. Defaults to None.
            duration(int): the last time for the test. Defaults to 60 seconds.
            start_delay(float): different lines start one by one with delay, if set 0, all the connection will start at the same time.
        """
        net = self.generate_network(n, bw, delay, loss, jitter)
        
        #create log dir name
        time_id = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        parameter_string = f"{cctype}_{n}hosts_delay={delay}_loss={loss}_bw={bw}_duration={duration}_start_delay={start_delay}_{KERNEL_VERSION}"
        print_t("stress", f"current Test: single cc algorithm test paramets: {parameter_string}")
        logs_dirname = f"./{LOG_PATH}" + time_id + "_" + parameter_string
        os.makedirs(logs_dirname, exist_ok=True)
        
        self.monitor_network(net.getNodeByName('s2'), logs_dirname, duration=duration)
        
        # run the tests
        cctypes = [cctype] * n
        self.run_test_by_ctype(cctypes, net, start_delay, logs_dirname, duration=duration)
                
        sleep(duration + 5 + start_delay * n )
        net.stop()
        
        if self.clean_log:
            self.clean_log(logs_dirname)
    
    def test_multi_cc(self, cc1, cc2, cc1_host_n=1, cc2_host_n=1, delay="10ms", loss=0, bw=10, jitter=None, duration=60, start_delay=0):
        """like test_single_cc, but use different cc algorithms on hosts
        Args:
            cc1 (_type_): first cc algorithm,  could be "cubic", "bbr", "copa", "reno", "bbrplus"
            cc2 (_type_): like cc2
            cc1_host_n (int, optional): number of hosts using first cc algorithm. Defaults to 1.
            cc2_host_n (int, optional): _description_. Defaults to 1.
            others: refer to test_single_cc parameters
        """
        net = self.generate_network(cc1_host_n + cc2_host_n, bw, delay, loss, jitter)
        
        #create log dir name
        time_id = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        parameter_string = f"{cc1}{cc1_host_n}_{cc2}{cc2_host_n}_delay={delay}_loss={loss}_bw={bw}_duration={duration}_start_delay={start_delay}_{KERNEL_VERSION}"
        print_t("stress", f"current Test: single cc algorithm test paramets: {parameter_string}")
        logs_dirname = "./logs/" + time_id + "_" + parameter_string
        os.makedirs(logs_dirname, exist_ok=True)
        
        self.monitor_network(net.getNodeByName('s2'), logs_dirname, duration=duration)
        
        # run the tests
        cctypes = [cc1] * cc1_host_n + [cc2] * cc2_host_n
        self.run_test_by_ctype(cctypes, net, start_delay, logs_dirname, duration=duration)
                
        sleep(duration + 5 + start_delay * (cc1_host_n + cc2_host_n)) #
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
        # start a new interactive cmd to debug
        if self.DEBUG:
            _thread.start_new_thread(lambda:CLI(net), () )
        return net

    def run_copa_test(self, senderHost, receiverHost, cctype, logs_dirname, duration):
        # for copa, use genericCC's sender/receiver scheme
        output_file = logs_dirname + f'/{senderHost.name}_copa.log'
        receiverHost.cmd(f'{genericCC_PATH}/receiver &')
        # print(f"{receiverHost.name} receiver init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

        senderHost.cmd(copa_sender_cmd(serverip=receiverHost.IP(), onduration=duration*1000, output_file=output_file))
        # print(f"{senderHost.name} sender init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

    def run_kernel_test(self, senderHost, receiverHost, cctype, logs_dirname, duration):
        # first set the tcp cc algorithm on host, duplicated since iperf3 can speficy the algorithm used
        # set_kernel_cc_algorithm(senderHost, cctype)
        
        # for cubic and bbr, use iperf scheme
        sender_output_file = logs_dirname + f'/{senderHost.name}_iperf.log'
        receiver_output_file = logs_dirname + f'/{receiverHost.name}_iperf.log'
        receiverHost.cmd(iperf_cmd(side="server", interval=0.1, output_file=receiver_output_file, verbose=True, json=True))
        # print(f"{receiverHost.name} receiver init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

        senderHost.cmd(iperf_cmd(address=receiverHost.IP(), time=duration, output_file=sender_output_file, interval=0.03,
                                 algorithm=cctype, verbose=True, json=True
                                 ))
        # print(f"{senderHost.name} sender init finished {time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}")

    def clean_log(self, logs_dirname):
        if self.clean_logs:
            del_list = os.listdir(logs_dirname)
            for file in del_list:
                os.remove(os.path.join(logs_dirname, file))
            os.removedirs(logs_dirname)
    
    def monitor_network(self, s2, logs_dirname, duration):
        """monitor the network traffic by commands

        Args:
            s2 (_type_): switch object
            logs_dirname (_type_): 
        """
        if self.monitor_type in ["ifstat", "both"]:
            s2.cmd(f'ifstat -t -a -z -l -n -T -b -q 0.1 {(duration+5) * 10} > {logs_dirname}/ifstat.log  2>&1 &')
        if self.monitor_type in ["ethstats", "both"]:
            s2.cmd(f'ethstats -t -n 1 -c {duration+5} > {logs_dirname}/ethstats.log  2>&1 &')
    
    def run_test_by_ctype(self, cctypes, net, start_delay, logs_dirname, duration):
        for _, cctype in enumerate(cctypes):
            i = _ + 1
            senderHost, receiverHost = net.getNodeByName(f'hs{i}', f'hr{i}')
            if cctype in ["cubic", "bbr", "bbrplus", "bbr2"]:
                _thread.start_new_thread(
                    CCTest.run_kernel_test, (self, senderHost, receiverHost, cctype, logs_dirname, duration)
                )
                # self.run_kernel_test(senderHost, receiverHost, cctype, logs_dirname, duration)
            elif cctype == "copa":
                _thread.start_new_thread(
                    CCTest.run_copa_test, (self, senderHost, receiverHost, cctype, logs_dirname, duration)
                )
                # self.run_copa_test(senderHost, receiverHost, cctype, logs_dirname, duration)
            else:
                print_t("warning", f"Unknown CC Algorithm: {cctype}")
            time.sleep(start_delay)
                    
if __name__ == '__main__':
    n = 3
    # duration = 30
    delay = "3ms"
    bw = 10 #mbps
    loss = 3
    jitter = "200ms"
        
    # use this line to write log to trash dir, easier to clean logs
    # LOG_PATH = "logs/trash/" 
    t = CCTest(clean_logs=False, DEBUG=False)
    
    t.test_single_cc("bbr", n=1, delay='40ms', loss=0, bw=100, jitter=None, duration=10)
    # t.test_multi_cc("copa", "cubic", cc1_host_n=1, cc2_host_n=1, duration=10, bw=bw, delay=delay, loss=loss)

    