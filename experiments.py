from testbed import *
from itertools import combinations, permutations

t = CCTest()
def test_single_algo_multi_delay(n=2, duration=30, bw=10, loss=0):
    for delay in ['0ms', '10ms', '100ms']:
        t.test_single_cc("cubic", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("bbr", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("copa", n=n, duration=duration, bw=bw, delay=delay, loss=loss)

def test_single_algo_multi_loss(n=2, duration=30, bw=10, delay='10ms'):
    for loss in [0, 0.3,  1, 3, 10, 20]:
        t.test_single_cc("cubic", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("bbr", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("copa", n=n, duration=duration, bw=bw, delay=delay, loss=loss)

def test_single_algo_multi_host(loss=3, duration=30, bw=10, delay='10ms'):
    for n in [2, 4, 10]:
        t.test_single_cc("cubic", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("bbr", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        t.test_single_cc("copa", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        
def test_multi_algo_multi_loss(cc1, cc2, cc1_host_n=1, cc2_host_n=1, duration=30, bw=10, delay='10ms'):
    for loss in [0, 3, 10]:
        t.test_multi_cc(cc1, cc2, cc1_host_n=cc1_host_n, cc2_host_n=cc2_host_n, duration=duration, bw=bw, delay=delay, loss=loss)

def test_multi_algo_multi_delay(cc1, cc2, cc1_host_n=1, cc2_host_n=1, duration=30, bw=10, loss=3):
    for delay in ['0ms', '10ms', '100ms']:
        t.test_multi_cc(cc1, cc2, cc1_host_n=cc1_host_n, cc2_host_n=cc2_host_n, duration=duration, bw=bw, delay=delay, loss=loss)
        
def test_multi_algo_multi_hosts(cc1, cc2, duration=30, bw=10, loss=3, delay='10ms'):
    for cc1_host_n, cc2_host_n in [(1,1), (1,3), (1,9)]:
        t.test_multi_cc(cc1, cc2, cc1_host_n=cc1_host_n, cc2_host_n=cc2_host_n, duration=duration, bw=bw, delay=delay, loss=loss)

if __name__ == '__main__':
    algos = ['cubic', 'bbr', 'copa', 
            #  'bbrplus'
             ]
    # for cc1, cc2 in combinations(algos, 2):
    #     test_multi_algo_multi_loss(cc1, cc2)
        
    # check if there is relationship between delay and throughput
    test_single_algo_multi_delay(n=2,  loss=0)
    test_single_algo_multi_delay(n=2,  loss=3)
    
    # check the throughput of different algorithms when loss rate get higher
    test_single_algo_multi_loss(n=2, delay='10ms')
    
    # check the fairness if multi hosts compete for one switch
    test_single_algo_multi_host(loss=3)
    test_single_algo_multi_host(loss=0)
    test_single_algo_multi_host(loss=1)

    
    # check the fairness if 2 hosts with different cc algos compete for one switch (in different loss)
    for cc1, cc2 in combinations(algos, 2):
        test_multi_algo_multi_loss(cc1, cc2)
    
    # check the fairness if 2 hosts with different cc algos compete for one switch (in different delay)
    for cc1, cc2 in combinations(algos, 2):
        test_multi_algo_multi_delay(cc1, cc2)

    # check the fairness if multi hosts with different cc algos compete for one switch (in different hosts rate)
    for cc1, cc2 in permutations(algos, 2):
        test_multi_algo_multi_hosts(cc1, cc2)