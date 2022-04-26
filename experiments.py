from testbed import *
from itertools import combinations, permutations

t = CCTest()
def test_single_algo_multi_delay(n=2, duration=30, bw=10, loss=0):
    for delay in ['0ms', '10ms', '100ms']:
        t.test_single_cc("cubic", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("bbr", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("copa", n=n, duration=duration, bw=bw, delay=delay, loss=loss)

def test_single_algo_multi_loss(n=2, duration=30, bw=10, delay='20ms', algo=['cubic', 'bbr']):
    for loss in [0, 0.001, 0.01, 0.1, 1, 1, 2, 5, 10, 20, 30]:
        for ctype in algo:
            t.test_single_cc(ctype, n=n, duration=duration, bw=bw, delay=delay, loss=loss)


def test_single_algo_multi_host(loss=3, duration=30, bw=10, delay='20ms', algo=['cubic', 'bbr'], start_delay=0.5):
    for n in [2, 3, 4, 5]:
        for ctype in algo:
            t.test_single_cc(ctype, n=n, duration=duration, bw=bw, delay=delay, loss=loss, start_delay=start_delay)

        
def test_multi_algo_multi_loss(cc1, cc2, cc1_host_n=1, cc2_host_n=1, duration=30, bw=10, delay='10ms'):
    for loss in [0, 3, 10]:
        t.test_multi_cc(cc1, cc2, cc1_host_n=cc1_host_n, cc2_host_n=cc2_host_n, duration=duration, bw=bw, delay=delay, loss=loss)

def test_multi_algo_multi_delay(cc1, cc2, cc1_host_n=1, cc2_host_n=1, duration=30, bw=10, loss=3):
    for delay in ['0ms', '10ms', '100ms']:
        t.test_multi_cc(cc1, cc2, cc1_host_n=cc1_host_n, cc2_host_n=cc2_host_n, duration=duration, bw=bw, delay=delay, loss=loss)
        
def test_multi_algo_multi_hosts(cc1, cc2, duration=30, bw=10, loss=3, delay='20ms', start_delay=0):
    for cc1_host_n, cc2_host_n in [(1,1)]:
        t.test_multi_cc(cc1, cc2, cc1_host_n=cc1_host_n, cc2_host_n=cc2_host_n,
                        duration=duration, bw=bw, delay=delay, loss=loss, start_delay=start_delay)

if __name__ == '__main__':
    # 测试bbr和cubic 不同loss下的表现
    test_single_algo_multi_loss(n=1)
    
    # 测试多个bbr同时竞争
    test_single_algo_multi_host(loss=0.01, algo=['bbr'], start_delay=2)
    test_single_algo_multi_host(loss=0.01, algo=['bbr'], start_delay=1)
    
    # 测试bbr和cubic的竞争效果
    test_multi_algo_multi_hosts('cubic', 'bbr', loss=0.001)
    test_multi_algo_multi_hosts('cubic', 'bbr', loss=0.1)