import os, argparse, re, csv
from tqdm import tqdm

INVALID = -1

def get_fn_params(fn):
    x = re.search(r'([a-z]*)_n([0-9]*)_s([0-9]*)_u([0-9]*).txt', fn)
    if x is None:
        return INVALID
    else:
        return {"prefix":x.group(1), "dim":int(x.group(2)), "seed":int(x.group(3)), "maxiter":int(x.group(4))}

def extract_info(s):
    s_inline = s.replace('\n', ' ')
    res = float(re.search('Solution: f\(\[.*?\]\) = ([0-9\.]*)', s_inline).group(1))
    user_time = float(re.search('User Time: ([0-9\.]*)', s_inline).group(1))
    sys_time = float(re.search('System Time: ([0-9\.]*)', s_inline).group(1))
    return {"result":res, "usertime":user_time, "systime":sys_time}

def write_to_csv(dict_data, fn):
    with open(fn, 'w') as csvfile:
        csv_columns = dict_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)

def main(args):
    file_list = os.listdir(args.dir)
    data = []
    for fn in tqdm(file_list):
        params = get_fn_params(fn)
        if params != INVALID:
            with open(os.path.join(args.dir, fn), 'r') as fp:
                content = fp.read()
            info = extract_info(content)
            params.update(info)
            data.append(params)
    write_to_csv(data, args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='set working directory', required=True)
    parser.add_argument('-o', '--output', help='set output .CSV file name', required=True)
    args = parser.parse_args()
    main(args)