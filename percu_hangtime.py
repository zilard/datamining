#!/usr/bin/python

from itertools import islice
import time
import subprocess
import os
import re
import copy
from datetime import datetime

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



COMP_CSV = "funcstat_comp23.csv"
HANG_LOG = "hangtimestamps.log"

VCPUS = 5


F_LIST = ["kvm_irqfd+"]

f_dict = {}

time_set = set()

KPROBE_PRETTYPRINT = True
KPROBE_PRETTYOUTLOG = "comp23_kprobe.log"


KPROBE_LOGS = [
"irqfd_cleanup_m4kxhpsrtc23.pve.tacn.detemobil.de_2021-02-25_17_10_59.log",
]


"""
KPROBE_LOGS = [
"irqfd_cleanup_m4kxhpsrtc23.pve.tacn.detemobil.de_2021-02-25_17_10_59.log"
]
"""


#=================================================

HANG_CSV = "hang.csv"

VCPU_LIST = ['0', '1', '2', '3']


UPTIME_LOGS = [
"CPU0_FSB1_20022025.log",
"CPU1_FSB1_20022025.log",
"CPU2_FSB1_20022025.log",
"CPU3_FSB1_20022025.log",
]


"""
UPTIME_LOGS = [
"CPU0_FSB1_20022025.log",
]
"""

percpu_hang_dict = {}
check_interval = 0.6

uptime_hang_set = set()

#==================================================



KERNLOG_DATETIME = "2021-02-23T19:37:17"
KERNLOG_UPTIMESECS = "119087.958403"


def hangtimestamps_crunch():
   
    DATE_PREFIX = "0225"
    F = "hangtimestamps"
    f_dict[F] = {}

    with open(HANG_LOG, 'r') as logfile:
        while True:
            line = logfile.readline()
            if line:
                date = int(DATE_PREFIX + ''.join(line.rstrip('\n').split(':')))
                time_set.add(date)
                cpu_bit_array = VCPUS * [0]
                cpu_bit_array[0] = 1
                f_dict[F][date] = copy.deepcopy(cpu_bit_array)

            else:
                break


DATE_CALC_CMD = "date -d'%s - %s seconds + %s seconds'"



def calc_timestamp(uptime_secs, dateformat=" +%m%d%H%M%S"):

    return exec_cmd(DATE_CALC_CMD % (KERNLOG_DATETIME, KERNLOG_UPTIMESECS, uptime_secs) + dateformat)




def uptimelog_crunch(uptime_log, append=False):


    lineno = 0
    startline_no = 4

    prev_uptime = 0.0
    prev_date = 0

    with open(uptime_log, 'r') as logfile:

        while True:

            line = logfile.readline()

            if line:

                if "Running on" in line:
                    lineno = 0
                    prev_uptime = 0.0

                lineno += 1

                if lineno >= startline_no:

                    pline = parse(line.rstrip('\n'))

                    cur_uptime = float(pline[4].split(':')[1])
                    cur_date = int( ''.join(pline[2].split('-')[1:]) + ''.join(pline[3].split('.')[0].split(':')) )

                    if prev_uptime != 0.0:
                        diff = cur_uptime - prev_uptime
                        if diff > check_interval:
                            cpu = pline[1].rstrip(':')                     
                            percpu_hang_dict[cpu].append(prev_date)
                            uptime_hang_set.add(prev_date)
                     
                    prev_uptime = cur_uptime
                    prev_date = cur_date
       

            else:
                break
                            







def kprobelog_crunch(kprobe_log, append=False):

    pretty_list = []
    result_list = []
    pretty_dateformat=" +\"%Y-%m-%d %H:%M:%S\"" 

    lineno = 0
    startline_no = 6

    cpu_bit_array = VCPUS * [0]

    print(kprobe_log)

    with open(kprobe_log, 'r') as logfile:

        while True:

            line = logfile.readline()

            lineno += 1

            if line:

                if lineno >= startline_no and KPROBE_PRETTYPRINT:
                    prettyline = []
                    pline = parse(line.rstrip('\n'))

                    if "CPU" in pline[0]:
                        uptime_secs = pline[4].rstrip(':')
                        prettyline.append(calc_timestamp(uptime_secs, pretty_dateformat))
                        prettyline.append(' '.join(pline[:2]))
                        prettyline += pline[5:]
                        pretty_list.append(prettyline)

                    if "kworker" in pline[0]:
                        uptime_secs = pline[3].rstrip(':')
                        prettyline.append(calc_timestamp(uptime_secs, pretty_dateformat))
                        prettyline.append(pline[0])
                        prettyline += pline[4:]
                        pretty_list.append(prettyline)


                for f in F_LIST:

                   if f in line:

                       pline = parse(line.rstrip('\n'))

                       if "CPU" in pline[0]:
                           cpu = int(pline[1].split('/')[0])
                           uptime_secs = pline[4].rstrip(':')
                           date = int(calc_timestamp(uptime_secs))

                           if f in f_dict:
                               if date in f_dict[f]:
                                   f_dict[f][date][cpu] += 1
                               else:
                                   time_set.add(date)
                                   cpu_bit_array[cpu] = 1
                                   f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                                   cpu_bit_array = VCPUS * [0]

                           else:
                               time_set.add(date)
                               cpu_bit_array[cpu] = 1
                               f_dict[f] = {}
                               f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                               cpu_bit_array = VCPUS * [0]


                       if "kworker" in pline[0]:

                           uptime_secs = pline[3].rstrip(':')
                           date = int(calc_timestamp(uptime_secs))

                           cpu = -1

                           if f in f_dict:

                               if date in f_dict[f]:
                                   f_dict[f][date][cpu] += 1
                               else:
                                   time_set.add(date)
                                   cpu_bit_array[cpu] = 1
                                   f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                                   cpu_bit_array = VCPUS * [0]

                           else:
                               time_set.add(date)
                               cpu_bit_array[cpu] = 1
                               f_dict[f] = {}
                               f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                               cpu_bit_array = VCPUS * [0]


            else:
                break


    if KPROBE_PRETTYPRINT: 
        pretty_list.append(['=' * 60])


    if KPROBE_PRETTYPRINT:
        write_operation = 'w'
        if append:
            write_operation = 'a+'
        with open(KPROBE_PRETTYOUTLOG, write_operation) as prettylog:
            for prettyline in pretty_list:
                prettylog.write("%s\n" % ' '.join(prettyline))



def stri(time):
    str_time = str(time)
    if len(str_time) == 9:
        str_time = '0' + str_time
    return str_time



def hang_stri(time):
    str_time = str(time)
    if len(str_time) != 10:
        str_time = '0' + str_time
    return (str_time)



def log_crunch():

    t_list = sorted(time_set)

    stat_list = []

    for t in t_list:

        bit_list = len(F_LIST) * VCPUS * [0]

        for f in F_LIST:
            if t in f_dict[f]:

                f_idx = F_LIST.index(f)
                bit_list[VCPUS*f_idx:VCPUS*f_idx+VCPUS] = f_dict[f][t]

        stat_list.append([stri(t)] +
                         [str(b) for b in bit_list])




    with open(COMP_CSV, 'w') as f:
        for stat in stat_list:         
            f.write("%s\n" % ','.join(
                                      stat
                                     ))
 




def hanglog_crunch():

    t_list = sorted(uptime_hang_set)

    stat_list = []

    for t in t_list:

        bit_list =  len(VCPU_LIST) * [0]

        for vcpu in VCPU_LIST:
            if t in percpu_hang_dict[vcpu]:
                v_idx = VCPU_LIST.index(vcpu)
                bit_list[v_idx] = 1

          
        stat_list.append([hang_stri(t)] +
                         [str(b) for b in bit_list])



    with open(HANG_CSV, 'w') as f:
        for stat in stat_list:         
            f.write("%s\n" % ','.join(
                                      stat
                                     ))




def main():

    append = False
    for vcpu in VCPU_LIST:
        percpu_hang_dict[vcpu] = []
    for uptime_log in UPTIME_LOGS:
        idx = UPTIME_LOGS.index(uptime_log)
        if idx > 0:
            append = True
        else:
            append = False
        uptimelog_crunch(uptime_log, append)

    hanglog_crunch()


    #F_LIST.append("hangtimestamps")
    #hangtimestamps_crunch()

    #log_crunch()



if __name__ == '__main__':
    main()



