genericCC_PATH = '~/Desktop/genericCC'

def iperf_cmd(side="client",address="", interval=1, port=None, time=15, window_size=None, output_file="",
              verbose=True, json=True, algorithm=None):
    """a tool for concating parameters for iperf command, return the command string
        further parameters explanation found in https://iperf.fr/iperf-doc.php
    Args:
        side (str, optional): clinet or server. Defaults to client.
        address (str, optional): Only for client side, the address of target server. Defaults to "".
        interval (int, optional):Only for client side,  the interval of showing bandwidth, at least 0.1. Defaults to '1' second.
        port (_type_, optional): The port to communicate. Defaults to None(5001).
        time (int, optional): test last time(seconds), only for sender. Defaults to 15.
        window_size (_type_, optional): the TCP window Size. Defaults to None.
        algorithm: Specify the tcp congestion control algorithm to use (cubic, reno, bbr), bbr2 only available on kernel with bbr2
        json: output in format of json file
        verbose: output information in details
    Returns:
        _type_: _description_
    """
    command = "iperf3 "
    if side == "server":
        command += "-s "
        if port:
            command += f"-p {port} "
    else:
        command += "-c "
        if address:
            command += f"{address} "
        if time:
            command += f"-t {time} "
        if algorithm:
            command += f"-C {algorithm} "
        
    if interval:
        command += f"-i {interval} "
    if window_size:
        command += f"-w {window_size} "
    if output_file:
        command += f"--logfile {output_file} "
    if verbose:
        command += "-V "
    if json:
        command += "-J "
    
    return command + "&"

def copa_sender_cmd(serverip="", offduration=0, onduration=10000, 
                    cctype="markovian", delta="0.5",
                    num_cycles=1, output_file=""
                    ):
    """
    run sender side genericCC command. Sender will automatically switch on(onduration) and off(offduration) repeatedly.
    One switch on and off can be seen as a cycle.
    eg.'onduration=10000 offduration=0 num_cycles=1': Switches on for 10 seconds and exits.
    more details on https://github.com/venkatarun95/genericCC#traffic

    Args:
        serverip (str, optional): server address ip. Defaults to "".
        offduration (int, optional): swtich off time. Defaults to 0(ms).
        onduration (int, optional): swtich on time. Defaults to 10000(ms).
        cctype (str, optional): algorithm used in sender.'cctype=[remy|markovian|kernel|tcp]'. 
            'markovian' denotes Copa, 'kernel' denotes the kernel's default tcp run using iperf and tcp denotes a simple AIMD algorithm. 
            Defaults to "markovian".
        delta (str, optional): The delta parameter for copa algorithm. Defaults to "do_ss:auto:0.5".
        num_cycles (int, optional): num of cycles. Defaults to 1.
        output_file (str, optional): the file save the output of sender. Defaults to "".
    """
    command = f'{genericCC_PATH}/sender '
    if serverip:
        command += f'serverip={serverip} '
    if offduration is not None:
        command += f'offduration={offduration} ' # if not pass, will set default 5000
    if onduration:
        command += f'onduration={onduration} ' 
    if cctype:
        command += f'cctype={cctype} '
    if delta:
        command += f'delta_conf=do_ss:auto:{delta} '
    if num_cycles:
        command += f'traffic_params=deterministic,num_cycles={num_cycles} '
    if output_file:
        command += f'> {output_file} 2>&1 '
    return command + "&"

def set_kernel_cc_algorithm(host, algorithm):
    """set the cc algorithm on host kernel

    Args:
        host (_type_): host of net
        algorithm (_type_): available kernel tcp congestion control algorithm: cubic, bbr, reno
    """
    print("Setting the Congestion Control Algorithm For {} = {}".format(host.name, algorithm))
    result = host.cmd("sysctl -w net.ipv4.tcp_congestion_control={}".format(algorithm))
    
    print("Setting Result: ", result)

def print_t(t="info", message=""):
    if t == "info":
        m = f"\033[0;30m{message}\033[0m"
    elif t == "warning":
        m = f"\033[0;31m{message}\033[0m"
    elif t == "stress":
        m = f"\033[0;32m{message}\033[0m"
    print(m)
    return m
    
    
    
    
    
    
    
    
    
    
    
if __name__ == '__main__':
    print(iperf_cmd(isClient=True, address="10.0.0.1"))
    print(copa_sender_cmd("10.0.0.1", output_file="logs/name.txt"))
    