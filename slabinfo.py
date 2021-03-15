
#!/usr/bin/python

from datetime import datetime
from itertools import islice
import time
import subprocess
import os
import re
import sys


SLABINFO_CMD = "cat /proc/slabinfo"
SLABINFO_CSV = "slabinfo.csv"

SLEEP_TIME = 1

TYPE = ['xfs_dqtrx', 'xfs_dquot', 'xfs_icr', 'xfs_ili', 'xfs_inode', 'xfs_da_state', 
        'xfs_log_ticket', 'blkdev_queue', 'blkdev_requests', 'bdev_cache']

LOC = { 'active_objs': 1,
        'num_objs': 2,
        'active_slabs': 13,
        'num_slabs': 14 }

SLABINFO_PRINTOUT_OFFSET = 2
    

def parse(printout):
    parsed_list = []
    parsed = []
    for l in printout.strip().splitlines()[SLABINFO_PRINTOUT_OFFSET:]:
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




def slabinfo_parse(parse_cmd):
    res = []
    r = parse(exec_cmd(parse_cmd))

    for line in r:

        if line[0] in TYPE:

            """
            print("%s\n" % line) 
            print("active_objs %s\n" % line[LOC['active_objs']])
            print("num_objs %s\n" % line[LOC['num_objs']])
            print("active_slabs %s\n" % line[LOC['active_slabs']])
            print("num_slabs %s\n" % line[LOC['num_slabs']])
            """

            res +=  [line[LOC['active_objs']],
                     line[LOC['num_objs']],   
                     line[LOC['active_slabs']],
                     line[LOC['num_slabs']]]

    #print("%s" % res)

    return sum(map(int, res)), res




def main():
 
    prev = 0
    idx = 0
   
    #print("%s\n" % slabinfo_parse(SLABINFO_CMD))


    with open(SLABINFO_CSV, 'w') as f:

        while True:
            now = datetime.now()
            date = now.strftime('%Y%m%d%H%M%S')

            sumres, res = slabinfo_parse(SLABINFO_CMD)
          
            if sumres != prev:
               prev = sumres
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

