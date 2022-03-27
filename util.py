
def iperf_cmd(side="client",address="", interval=1, port=None, time=15, window_size=None, output_file=""):
    """a tool for concating parameters for iperf command, return the command string
        further parameters explanation found in https://iperf.fr/iperf-doc.php
    Args:
        side (str, optional): clinet or server. Defaults to client.
        address (str, optional): Only for client side, the address of target server. Defaults to "".
        interval (int, optional):Only for client side,  the interval of showing bandwidth. Defaults to '1' second.
        port (_type_, optional): The port to communicate. Defaults to None(5001).
        time (int, optional): test last time(seconds). Defaults to 15.
        window_size (_type_, optional): the TCP window Size. Defaults to None.

    Returns:
        _type_: _description_
    """
    command = "iperf "
    if side == "server":
        command += "-s "
        if port:
            command += f"-p {port} "
    else:
        command += "-c "
        if address:
            command += f"{address} "
        if interval:
            command += f"-i {interval} "
        if time:
            command += f"-t {time} "
        if window_size:
            command += f"-w {window_size} "
        if output_file:
            command += f"> {output_file} 2>&1 "
    return command + "&"


genericCC_PATH = '~/Desktop/genericCC'

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
    if offduration:
        command += f'offduration={offduration} '
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
    result = host.cmd("sysctl net.ipv4.tcp_congestion_control={}".format(algorithm))
    
    print("Setting Result: ", result)
    


if __name__ == '__main__':
    print(iperf_cmd(isClient=True, address="10.0.0.1"))
    print(copa_sender_cmd("10.0.0.1", output_file="logs/name.txt"))
    