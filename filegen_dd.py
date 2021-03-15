#!/usr/bin/python

from datetime import datetime
from itertools import islice
import time
import subprocess
import os
import re
import sys
import glob


DF_CMD = "df -a ."
MB100 = 100 * 1024 * 1024
MULTIPLIER = 5
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



def available(parse_cmd):
    r = parse(exec_cmd(parse_cmd))
    return int(r[1][3]) * 1024



def main():

    cwd = os.getcwd()
    PATH = cwd + '/FILES'
    if not os.path.exists(PATH):
        os.mkdir(PATH)

    idx = 0


    if PATH:
        if os.listdir(PATH):
            os.system("rm %s/*" % PATH)
 
    while True:

        avail = available(DF_CMD)

        if (avail > (MULTIPLIER * MB100)):

            if not os.path.exists(PATH):
                os.mkdir(PATH)

            '''
            with open(PATH + "/" + str(idx), 'wb') as f:
                f.write(os.urandom(MB100)) 
            '''
 
            cmd = "dd if=/dev/urandom of=%s bs=100M count=4" % (PATH + "/" + str(idx))
            exec_cmd(cmd)

            idx += 1
            print("file created => %s\n" % idx)

        else:

            if PATH:
                print("MAX STORAGE REACHED - CLEARING %s/*\n" % PATH)
                os.system("rm %s/*" % PATH)
            idx = 0


        time.sleep(SLEEP_TIME)




if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        sys.exit(0)

