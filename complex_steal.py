#!/usr/bin/python

from datetime import datetime
from itertools import islice
import time
import subprocess
import os
import re
import sys


PROCSTAT_CMD = "cat /proc/stat | grep 'cpu'"
STEAL_CSV = "steal.csv"

SLEEP_TIME = 1


def parse(printout):
    parsed_list = []
    parsed = []
    for l in printout.strip().splitlines():
        parsed = []

        cluttered = [e.strip() for e in l.split(' ')]

        for p in cluttered:
            if p:
                parsed.append(p)
        if len(parsed):
            parsed_list.append(parsed)
    return parsed if len(parsed_list) == 1 else parsed_list




def exec_cmd(cmd, check=False):
    nul_f = open(os.devnull, 'w')
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=nul_f,
                               shell=True)
    nul_f.close()
    response = process.communicate()[0].strip()
    return response




def procstat_parse(parse_cmd):
    res = []
    r = parse(exec_cmd(parse_cmd))[1:]
    for line in r:
        res.append([int(i) for i in line[1:]])
    return res



def get_per_cpu_interval(prev_res, res):

    ishift = 0

    user = res[0]
    nice = res[1]
    sys = res[2]
    idle = res[3]
    iowait = res[4]
    hardirq = res[5]
    softirq = res[6]
    steal = res[7]
    guest = res[8]
    guest_nice = res[9]

    prev_user = prev_res[0]
    prev_nice = prev_res[1]
    prev_sys = prev_res[2]
    prev_idle = prev_res[3]
    prev_iowait = prev_res[4]
    prev_hardirq = prev_res[5]
    prev_softirq = prev_res[6]
    prev_steal = prev_res[7]
    prev_guest = prev_res[8]
    prev_guest_nice = prev_res[9]


    if ((user - guest) < (prev_user - prev_guest)):
        ishift += (prev_user - prev_guest) - (user - guest)

    if ((nice - guest_nice) < (prev_nice - prev_guest_nice)):
        ishift += (prev_nice - prev_guest_nice) - (nice - guest_nice)


    return ((user + nice +
             sys + iowait +
             idle + steal +
             hardirq + softirq) -
            (prev_user + prev_nice +
             prev_sys + prev_iowait +
             prev_idle + prev_steal +
             prev_hardirq + prev_softirq) +
             ishift)





def calc(prev_res, res):

    ret = []

    for cpu_idx in range(len(res)):

        itv = get_per_cpu_interval(prev_res[cpu_idx], res[cpu_idx])
        steal = res[cpu_idx][7]
        prev_steal = prev_res[cpu_idx][7]

        ret.append(ll_sp_value(prev_steal, steal, itv))

    return ret



def ll_sp_value(value1, value2, itv):

    if ((value2 < value1) and (value1 <= 0xffffffff)):
   
        return float((value2 - value1) & 0xffffffff) / itv * 100

    else:

        return float(value2 - value1) / itv * 100



def main():
 
    idx = 0
 
    prev_res = []
  
    with open(STEAL_CSV, 'w') as f:

        while True:

            now = datetime.now()
            date = now.strftime('%Y%m%d%H%M%S')

            res = procstat_parse(PROCSTAT_CMD)
          

            if prev_res:

                calc_res = calc(prev_res, res)
                calc_res_str = [format(i,'.2f') for i in calc_res]

                idx += 1
                     
                print("%s\n" % calc_res_str)

                f.write("%s\n" % ','.join([
                                           str(idx),
                                           date
                                          ] +
				          calc_res_str
                                         ))
            else:

                prev_res = res



            time.sleep(SLEEP_TIME)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


