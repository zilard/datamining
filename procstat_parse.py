#!/usr/bin/python

from itertools import islice
import time
import subprocess
import os
import re

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

VM_FILE = "vm-collect-iocpu.log_20210209_111815"
PROCSTAT_CSV = "procstat.csv"



def datacrunch():

    date_start = "____DATE"
    procstat_start = "____PROC_STAT"

    procstat = []
    procstat_list = []


    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    procstat_rec_started = False
    procstat_lineno = 0
    procstat_maxline = 6

    date = ""




    with open(VM_FILE, 'r') as f:
        while True:
            line = f.readline()
            if line:

                if date_start in line:
                    date = ""
                    date_rec_started = True
                
                if date_rec_started:
                    date_lineno += 1

                    if date_lineno == date_maxline:
	                date = line.rstrip('\n')
                        date_rec_started = False
                        date_lineno = 0


                if procstat_start in line:
                    procstat_rec_started = True
                    procstat = [date]
                
                     

                
                if procstat_rec_started:
                    procstat_lineno += 1

                    if procstat_lineno > 2:
                        procstat_line = parse(line.rstrip('\n'))

                        #print("DATE: %s  PROCSTAT_LINE: %s" % (date, procstat_line[1:8])) 
                
                        interval = sum(map(int, procstat_line[1:8]))

                        #print("INTERVAL: %s" % interval)

                        #print("user:%s interval:%s usr:%s" % (procstat_line[1], interval, ((float(procstat_line[1])/interval) * 100)))
                        usr = "%.2f" %  ((float(procstat_line[1])/interval) * 100)
                        sys = "%.2f" %  ((float(procstat_line[3])/interval) * 100)
                        iowait = "%.2f" %  ((float(procstat_line[5])/interval) * 100)
                        steal = "%.2f" %  ((float(procstat_line[8])/interval) * 100)
                         
                        #print("usr %s / sys %s / iowait %s / steal %s" % (usr, sys, iowait, steal))

                        procstat = procstat + [usr, sys, iowait, steal]


                        if procstat_lineno == procstat_maxline:
                            procstat_rec_started = False
                            procstat_lineno = 0
                            procstat_list.append(procstat)
                            procstat = []


            else:
                break



    with open(PROCSTAT_CSV, 'w') as f:
        for procstat in procstat_list:
            i = procstat_list.index(procstat)
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      procstat
                                     ))
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()




