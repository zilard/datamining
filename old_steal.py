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
        res.append(line[8])

    return res




def main():
 
    idx = 0
   
    with open(STEAL_CSV, 'w') as f:

        while True:
            now = datetime.now()
            date = now.strftime('%Y%m%d%H%M%S')

            res = procstat_parse(PROCSTAT_CMD)
          
            idx += 1
             
            print("%s\n" % res)

            f.write("%s\n" % ','.join([
                                       str(idx),
                                       date
                                      ] +
                                      res
                                     ))

            time.sleep(SLEEP_TIME)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

