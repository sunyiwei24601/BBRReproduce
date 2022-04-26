import os
from torch.utils.tensorboard import SummaryWriter
import csv
import collections

def classify_logs(filename='analysis_send.csv'):
    reader = csv.DictReader(open(filename))
    dic = collections.defaultdict(dict)
    for row in reader:
        """seperate rows by hosts and experiment_ids
        e.g. {
            's1-eth1': {
                'experimnet_1': [row1, row2],
                'experiment_2': [row3, row4]
            }
        }
        """
        host = row['host'].split("_")[0]
        tag = row['experiment_id']
        row['start'] = float(row['start'])
        row['bytes'] = int(row['bytes'])
        row['bits_per_second'] = int(float(row['bits_per_second']))
        row['snd_cwnd'] = int(row['snd_cwnd'])
        row['rtt'] = int(row['rtt'])
        if not dic[host].get(tag):
            dic[host][tag] = [row]
        else:
            dic[host][tag].append(row)
    return dic

def write_tf_logs(dic):
    TF_LOG_PATH = "tf_send_logs"
    if os.path.exists(TF_LOG_PATH):
        os.system(f"rm -rf {TF_LOG_PATH}/*")
    for host in dic:
        writer = SummaryWriter(os.path.join(TF_LOG_PATH, host))
        for experiment_rows in dic[host].values():
            timestamps = [int(_['start']*100) for _ in experiment_rows]
            start_timestamp = min(timestamps)
            experiment_rows = sorted(experiment_rows, key=lambda x:x['start'])
            for row in experiment_rows:
                step = int(row['start'] * 100)
                experiment_id = row['experiment_id']
                writer.add_scalar(f"{experiment_id}/RTT", row['rtt'], step)
                writer.add_scalar(f"{experiment_id}/Throughput", row['bits_per_second'], step)
                writer.add_scalar(f"{experiment_id}/cwnd", row['snd_cwnd'], step)

        writer.flush()
        writer.close()
if __name__ == '__main__':
    result = classify_logs()
    write_tf_logs(result)
    