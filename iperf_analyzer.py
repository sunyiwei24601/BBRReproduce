import json
import csv
import os

rec_log_file = "analysis_rec.csv"
send_log_file = "analysis_send.csv"
logs_path = "./logs"

def extract_iperf_rec_log(filename):
    with open(filename) as f:
        data = json.load(f)
    start = data['start']
    start_timestamp = start['timestamp']['timesecs']
    records = [_['sum'] for _ in data['intervals']]
    n = 0
    for i in records:
        if i['bits_per_second'] != 0:
            break
        n+=1
    return records[n:]

def extract_iperf_send_log(filename):
    with open(filename) as f:
        data = json.load(f)
    start = data['start']
    start_timestamp = start['timestamp']['timesecs']
    records = [_['streams'][0] for _ in data['intervals']]
    n = 0
    return records[n:]


def extract_save_send_log(dirnames):
    #write the header first
    send_fieldnames = ['experiment_id', 'host', 'start', 'bytes', 'bits_per_second', 'retransmits', 'snd_cwnd', 'snd_wnd', 'rtt', 'rttvar', 'socket', 'end', 'seconds', 'omitted', 'pmtu', 'sender']
    with open(send_log_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=send_fieldnames)
        writer.writeheader()
    
        for dirname in dirnames:
            if dirname == 'trash':
                continue
            filenames = os.listdir(os.path.join(logs_path, dirname))
            filenames = [filename for filename in filenames if filename[:2] == "hs"]
            for filename in filenames:
                records = extract_iperf_send_log(os.path.join(logs_path, dirname, filename))
                for record in records:
                    record['host'] = filename
                    record['experiment_id'] = dirname
                    writer.writerow(record)

def extract_save_rec_log(dirnames):
    #write the header first
    send_fieldnames = ['experiment_id', 'host', 'start', 'end', 'bytes', 'bits_per_second', 'socket', 'omitted', 'sender', 'seconds']
    with open(rec_log_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=send_fieldnames)
        writer.writeheader()
    
        for dirname in dirnames:
            if dirname == 'trash':
                continue
            filenames = os.listdir(os.path.join(logs_path, dirname))
            filenames = [filename for filename in filenames if filename[:2] == "hr"]
            for filename in filenames:
                records = extract_iperf_rec_log(os.path.join(logs_path, dirname, filename))
                for record in records:
                    record['host'] = filename
                    record['experiment_id'] = dirname
                    
                    writer.writerow(record)

if __name__ == '__main__':
    dirnames = os.listdir(logs_path)
    extract_save_send_log(dirnames)
    extract_save_rec_log(dirnames)
