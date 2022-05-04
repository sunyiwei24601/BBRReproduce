import csv
import os
import collections
import json
from util import *
repository_dir = "/home/kyle/Desktop/CopaReproduce"
logs_path = f"{repository_dir}/logs"

log_ethstats_file = "analysis_second.csv"
log_ifstat_file = 'analysis_microsecond.csv'
fieldnames = ['experiment_id','timestamp', 'host', 'in_num', 'in_unit', 'out_num', 'out_unit', 'in_pac_num', 'in_pac_unit',
        'out_pac_num', 'out_pac_unit']

def timestr2int(timestr):
    """convert time str into time int so we can calculate the time stamp
    possible bug: 11:59:59 will  be larger than 00:00:00
    05:04:22 -> 5 * 3600 + 4 * 60 + 22
    Args:
        timestr (_type_): timestr like "05:04:22"
    """
    parts = [int(_) for _ in timestr.split(':')]
    timeint = parts[0] * 3600 + parts[1] * 60 + parts[2]
    return timeint

def extract_ethstats_log(dirname):
    filename = f"{repository_dir}/logs/{dirname}/ethstats.log"
    if not os.path.exists(filename):
        return []
    f = open(filename)
    row = f.readline()

    result = []
    while(row):
        parts = row.split()
        # first total line has 15 parts, while others have only 14 parts
        # first line example:
        #    1648366318    total:    25.08 Mb/s In    24.85 Mb/s Out -   2088.0 p/s In    2161.0 p/s Out 
        # other line example:
        #                s1-eth1:     8.24 Mb/s In     0.18 Mb/s Out -    360.0 p/s In     344.0 p/s Out

        if len(parts) == 15:
            timestamp = parts[0]
            parts = parts[1:]
        # if timestamp in identified: #do not append record which is added before
        #     row  = f.readline()
        #     continue
        record = {
            "timestamp": timestamp,
            "host": parts[0][:-1], #remove :
            "in_num": parts[1],
            "in_unit": parts[2],
            "out_num": parts[4],
            "out_unit": parts[5],
            "in_pac_num": parts[8],
            "in_pac_unit": parts[9],
            "out_pac_num": parts[11],
            "out_pac_unit": parts[12],
            "experiment_id": dirname,  
        }
        result.append(record)   
        row  = f.readline()
    return result

def extract_ifstat_log(dirname):
    filename = f"{repository_dir}/logs/{dirname}/ifstat.log"
    if not os.path.exists(filename):
        return []
    
    f = open(filename)
    hosts = f.readline().split()
    header = f.readline().split()
    row  = f.readline()

    result = collections.defaultdict(lambda:collections.defaultdict(list))
    """result format like
    {
        'hostname':{
            '05:04:38': [(28.29, 28.29), (,)]
        } 
    }
    """
    while(row):
        parts = row.split()
        # first 2 lines example:
        #    Time            lo                 eth0              s1-eth1             s1-eth2              Total
        # HH:MM:SS   Kbps in  Kbps out   Kbps in  Kbps out   Kbps in  Kbps out   Kbps in  Kbps out   Kbps in  Kbps out 
        # other line example:
        # 05:04:38     28.29     28.29     13.09     23.84      0.00      0.00      0.00      0.00     41.38     52.13
        timestr = parts[0]
        if timestr == 'ifstat:':
            row = f.readline()
            continue
        timeint = timestr2int(timestr)
        for i, host in enumerate(hosts[1:]):
            in_num = parts[2*i+1]
            out_num = parts[2*i+2]
            in_num = 0 if in_num == 'n/a' else in_num
            out_num = 0 if out_num == 'n/a' else out_num

            result[host][timeint].append((in_num, out_num)) 
        row  = f.readline()
    
    output= []
    for host in result:
        records = result[host]
        for timeint in records:
            record_list = records[timeint]
            timestamp = (timeint+1) * 10 - 1 # split one second into ten 100 microseconds
            for in_num, out_num in reversed(record_list):
                record = {
                    "timestamp": timestamp,
                    "host": host,
                    "in_num": in_num,
                    "in_unit": 'Kb/s',
                    "out_num": out_num,
                    "out_unit": 'Kb/s',
                    "in_pac_num": 0,
                    "in_pac_unit": 'p/s',
                    "out_pac_num": 0,
                    "out_pac_unit": 'p/s',
                    "experiment_id": dirname,  
                }
                output.append(record)  
                timestamp -= 1
    return output

def extract_save_log(log_type='ifstat'):
    """read log dirs and save in analysis.csv

    Args:
        log_type (str, optional): record type ifstat or ethstats. Defaults to 'ifstat'.
    """
    if log_type == 'ifstat':
        logfile = log_ifstat_file
    else:
        logfile = log_ethstats_file
    
    #write the header first
    with open(logfile, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    
    dirnames = os.listdir(logs_path)
    csvfile = open(logfile, 'a')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    for dirname in dirnames:
        if dirname == 'trash':
            continue
        if log_type == 'ifstat':
            records = extract_ifstat_log(dirname)
        else:
            records = extract_ethstats_log(dirname)
        writer.writerows(records)
    csvfile.close()

if __name__ == '__main__':
    extract_save_log('ifstat')
    extract_save_log('ethstats')
