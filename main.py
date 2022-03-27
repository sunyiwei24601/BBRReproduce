from time import sleep
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo

MININET_PATH = '/root/mininet'


class MyTopo(Topo):
    def build(self):
        leftHosts = [self.addHost(f'ha{x}') for x in range(1, 12)]
        rightHosts = [self.addHost(f'hb{x}') for x in range(1, 12)]
        leftSwitch = self.addSwitch('sa1')
        rightSwitch = self.addSwitch('sb1')

        self.addLink(leftSwitch, rightSwitch)
        for host in leftHosts:
            self.addLink(host, leftSwitch)
        for host in rightHosts:
            self.addLink(rightSwitch, host)

topos = { 'mytopo': ( lambda: MyTopo() ) }

def main():
    topo = MyTopo()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()

    for i in range(2, 12):
        receiver = net[f'hb{i}']
        receiver.cmd(f'{MININET_PATH}/genericCC/receiver &')
        sender = net[f'ha{i}']
        sender.cmd(f'{MININET_PATH}/genericCC/sender serverip={receiver.IP()} offduration=1000 onduration=10000 cctype=tcp delta_conf=do_ss:auto:0.5 traffic_params=deterministic,num_cycles=1 > {MININET_PATH}/logs/sender-a{i}.txt 2>&1 &')
        sender.cmd(f'ethstats -t -n 1 -c 11 > {MININET_PATH}/logs/ethstats-a{i}.txt 2>&1 &')

    hb1 = net['hb1']
    hb1.cmd(f'{MININET_PATH}/genericCC/receiver &')
    ha1 = net['ha1']
    ha1.cmd(f'{MININET_PATH}/genericCC/sender serverip={hb1.IP()} offduration=1000 onduration=10000 cctype=markovian delta_conf=do_ss:auto:0.5 traffic_params=deterministic,num_cycles=1 >> {MININET_PATH}/logs/sender-a1.txt 2>&1 &')
    ha1.cmd(f'ethstats -t -n 1 -c 11 > {MININET_PATH}/logs/ethstats-a1.txt 2>&1 &')

    sleep(12)
    net.stop()


if __name__ == '__main__':
    main()