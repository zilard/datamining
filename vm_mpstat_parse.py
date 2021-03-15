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


VM_FILE = "vm-collect-iocpu.log_20210218_034620"
MPSTAT_CSV = "vm_mpstat_034620.csv"



def datacrunch():

    date_start = "____DATE"
    mpstat_start = "____MPSTAT"

    mpstat = []
    mpstat_list = []


    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    mpstat_rec_started = False
    mpstat_lineno = 0
    mpstat_maxline = 9

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
	                date = line.rstrip('\n').split('.')[0]
                        date_rec_started = False
                        date_lineno = 0

                if date:

                    if mpstat_start in line:
                        mpstat_rec_started = True
                        mpstat = [date]
                
                
                    if mpstat_rec_started:
                        mpstat_lineno += 1

                        if mpstat_lineno > 5:
                            mpstat_line = parse(line.rstrip('\n'))
                
                            usr = "%.2f" % float(mpstat_line[2])
                            sys = "%.2f" %  float(mpstat_line[4])
                            iowait = "%.2f" % float(mpstat_line[5])
                            hardirq = "%.2f" % float(mpstat_line[6])
                            softirq = "%.2f" % float(mpstat_line[7])
                            steal = "%.2f" % float(mpstat_line[8])
                         
                            mpstat += [usr, sys, iowait, hardirq, softirq, steal]

                            if mpstat_lineno == mpstat_maxline:
                                mpstat_rec_started = False
                                mpstat_lineno = 0
                                mpstat_list.append(mpstat)
                                mpstat = []


            else:
                break



    with open(MPSTAT_CSV, 'w') as f:
        for mpstat in mpstat_list:
            i = mpstat_list.index(mpstat)
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      mpstat
                                     ))
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()

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


VM_FILE = "vm-collect-iocpu.log_20210218_034620"
MPSTAT_CSV = "vm_mpstat_034620.csv"



def datacrunch():

    date_start = "____DATE"
    mpstat_start = "____MPSTAT"

    mpstat = []
    mpstat_list = []


    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    mpstat_rec_started = False
    mpstat_lineno = 0
    mpstat_maxline = 9

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
	                date = line.rstrip('\n').split('.')[0]
                        date_rec_started = False
                        date_lineno = 0

                if date:

                    if mpstat_start in line:
                        mpstat_rec_started = True
                        mpstat = [date]
                
                
                    if mpstat_rec_started:
                        mpstat_lineno += 1

                        if mpstat_lineno > 5:
                            mpstat_line = parse(line.rstrip('\n'))
                
                            usr = "%.2f" % float(mpstat_line[2])
                            sys = "%.2f" %  float(mpstat_line[4])
                            iowait = "%.2f" % float(mpstat_line[5])
                            hardirq = "%.2f" % float(mpstat_line[6])
                            softirq = "%.2f" % float(mpstat_line[7])
                            steal = "%.2f" % float(mpstat_line[8])
                         
                            mpstat += [usr, sys, iowait, hardirq, softirq, steal]

                            if mpstat_lineno == mpstat_maxline:
                                mpstat_rec_started = False
                                mpstat_lineno = 0
                                mpstat_list.append(mpstat)
                                mpstat = []


            else:
                break



    with open(MPSTAT_CSV, 'w') as f:
        for mpstat in mpstat_list:
            i = mpstat_list.index(mpstat)
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      mpstat
                                     ))
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()


