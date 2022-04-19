import os
from torch.utils.tensorboard import SummaryWriter
import csv
import collections
    
# reader = csv.DictReader(open('analysis.csv'))
reader = csv.DictReader(open('analysis_microsecond.csv'))
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
    host = row['host']
    tag = row['experiment_id']
    if not dic[host].get(tag):
        dic[host][tag] = [row]
    else:
        dic[host][tag].append(row) 


def write_tf_logs(aggregate_step=1):
    TF_LOG_PATH = "tf_logs"
    TF_LOG_PATH = TF_LOG_PATH + f"_{aggregate_step}"
    if os.path.exists(TF_LOG_PATH):
        os.system(f"rm -rf {TF_LOG_PATH}/*")
    for host in dic:
        writer = SummaryWriter(os.path.join(TF_LOG_PATH, host))
        for experiment_rows in dic[host].values():
            timestamps = [int(_['timestamp']) for _ in experiment_rows]
            start_timestamp = min(timestamps)
            experiment_rows = sorted(experiment_rows, key=lambda x:x['timestamp'])
            aggregated_rows = aggregate_rows(experiment_rows, aggregate_step=aggregate_step)
            for row in aggregated_rows:
                tag = row['experiment_id']
                step = int(row['timestamp']) - start_timestamp
                host = row['host']
                in_num = float(row['in_num'])
                out_num = float(row['out_num'])
                if row['in_unit'] == 'Kb/s':
                    in_num /= 1024 
                if row['out_unit'] == 'Kb/s':
                    out_num /= 1024 
                if host[:2] == 's2':
                    writer.add_scalar(tag, out_num, step)
                else:
                    writer.add_scalar(tag, in_num, step)
        writer.flush()
        writer.close()

def aggregate_rows(rows, aggregate_step=1):
    """aggregate the rows's in and out num together by aggregate step

    Args:
        rows (_type_): _description_
        aggregate_step (int, optional): _description_. Defaults to 1.
    """
    result = []
    for start in range(0, len(rows), aggregate_step):
        end = min(start + aggregate_step, len(rows))
        cur_rows = rows[start:end]
        in_num = sum([float(_['in_num']) for _ in cur_rows])/len(cur_rows)
        out_num = sum([float(_['out_num']) for _ in cur_rows])/len(cur_rows)
        cur_rows[0]['in_num'] = in_num
        cur_rows[0]['out_num'] = out_num
        result.append(cur_rows[0])
    return result
    

if __name__ == '__main__':
    write_tf_logs(10)
    