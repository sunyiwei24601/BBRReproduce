from testbed import *

def test_single_algo_multi_delay(n=2, duration=30, bw=10, loss=0):
    for delay in ['0ms', '10ms', '100ms']:
        test_single_cc("cubic", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        test_single_cc("bbr", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        test_single_cc("copa", n=n, duration=duration, bw=bw, delay=delay, loss=loss)

def test_single_algo_multi_loss(n=2, duration=30, bw=10, delay='10ms'):
    for loss in [0, 3, 10, 20]:
        test_single_cc("cubic", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        test_single_cc("bbr", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        test_single_cc("copa", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        
def test_single_algo_multi_host(loss=3, duration=30, bw=10, delay='10ms'):
    for n in [2, 4, 10]:
        test_single_cc("cubic", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        test_single_cc("bbr", n=n, duration=duration, bw=bw, delay=delay, loss=loss)
        test_single_cc("copa", n=n, duration=duration, bw=bw, delay=delay, loss=loss)