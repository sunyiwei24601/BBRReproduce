import csv
import os

from pip import main
repository_dir = "/home/kyle/Desktop/CopaReproduce"

log_stats_file = "analysis.csv"
identified = {}
fieldnames = ['experiment_id','timestamp', 'host', 'in_num', 'in_unit', 'out_num', 'out_unit', 'in_pac_num', 'in_pac_unit',
        'out_pac_num', 'out_pac_unit']

if os.path.exists(log_stats_file):
    with open(log_stats_file) as f:
        reader = csv.DictReader(f)
        for i in reader: # use timestamp as key to remove duplicated lines
            identified[i['timestamp']] = True
else:# if file not exist, write the header first
    with open(log_stats_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()



def extract_ethstats_log(dirname):
    filename = f"{repository_dir}/logs/{dirname}/ethstats.log"
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
        if timestamp in identified: #do not append record which is added before
            row  = f.readline()
            continue
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



if __name__ == '__main__':
    logs_path = f"{repository_dir}/logs"
    dirnames = os.listdir(logs_path)
    
    csvfile = open(log_stats_file, 'a')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    for dirname in dirnames:
        records = extract_ethstats_log(dirname)
        writer.writerows(records)
    csvfile.close()
