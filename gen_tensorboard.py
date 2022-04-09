import os
from torch.utils.tensorboard import SummaryWriter
import csv
import collections

TF_LOG_PATH = "tf_logs"
if os.path.exists(TF_LOG_PATH):
    os.system(f"rm -rf {TF_LOG_PATH}/*")

reader = csv.DictReader(open('analysis.csv'))
dic = collections.defaultdict(list)
for row in reader:
    dic[row['host']].append(row)
    
for host in dic:
    writer = SummaryWriter(os.path.join(TF_LOG_PATH, host))
    for row in dic[host]:
        tag = row['experiment_id']
        step = row['timestamp']
        host = row['host']
        in_num = float(row['in_num'])
        if row['in_unit'] == 'Kb/s':
            in_num /= 1024 
        writer.add_scalar(tag, in_num, step)
    writer.flush()
    writer.close()

    

