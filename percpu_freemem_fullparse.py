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



COMP_LOG = "compute_collect_20210225_142133.log"
COMP_CSV = "percpu_freemem_compstat_142133.csv"
HANG_LOG = "hangtimestamps.log"

STACK_LOG = "qemu_instance-000005be_25022021.log"

VCPUS = 5
F_LIST = ["kvm_irqfd+"]

f_dict = {}


KPROBE_LOGS = [
"irqfd_cleanup_m4kxhpsrtc23.pve.tacn.detemobil.de_2021-02-23_19_37_17.log",
"irqfd_cleanup_m4kxhpsrtc23.pve.tacn.detemobil.de_2021-02-25_17_10_59.log"
]


"""
KPROBE_LOGS = [
"irqfd_cleanup_m4kxhpsrtc23.pve.tacn.detemobil.de_2021-02-25_17_10_59.log"
]
"""

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
                cpu_bit_array = VCPUS * [0]
                cpu_bit_array[0] = 1
                f_dict[F][date] = copy.deepcopy(cpu_bit_array)

            else:
                break


DATE_CALC_CMD = "date -d'%s - %s seconds + %s seconds'"



def calc_timestamp(uptime_secs):

    return exec_cmd(DATE_CALC_CMD % (KERNLOG_DATETIME, KERNLOG_UPTIMESECS, uptime_secs) + " +%m%d%H%M%S")





def kprobelog_crunch(kprobe_log):

    result_list = []
 
    cpu = 0
    cpu_bit_array = VCPUS * [0]

    print(kprobe_log)

    with open(kprobe_log, 'r') as logfile:

        while True:

            line = logfile.readline()

            if line:

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
                                   cpu_bit_array[cpu] = 1
                                   f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                                   cpu_bit_array = VCPUS * [0]

                           else:
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
                                   cpu_bit_array[cpu] = 1
                                   f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                                   cpu_bit_array = VCPUS * [0]

                           else:
                               cpu_bit_array[cpu] = 1
                               f_dict[f] = {}
                               f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                               cpu_bit_array = VCPUS * [0]


            else:
                break




def stack_crunch():

    date_start = "===== "
    stack_start = "== CPU"

    date_rec_started = False
    date_lineno = 0
    date_maxline = 1
    date = ""


    stack_rec_started = False    
    stack_lineno = 0
     

    cpu_bit_array = VCPUS * [0]


    with open(STACK_LOG, 'r') as logfile:
        while True:
            line = logfile.readline()
            if line:

                if date_start in line:
                    date_rec_started = True
                    stack_rec_started = False
                    stack_lineno = 0
                
                if date_rec_started:
                    date_lineno += 1

                    if date_lineno == date_maxline:
	                #date = datetime.strptime(line.rstrip('\n')[1].split('.')[0], '%H:%M:%S')
                        date = int(''.join(parse(line.rstrip('\n'))[1].split('.')[0].split(':')))
                        date_rec_started = False
                        date_lineno = 0




                if stack_start in line:
                    stack_rec_started = True
                    stack_lineno = 0
                    cpu = int(parse(line.rstrip('\n'))[3])



                if stack_rec_started:
                    stack_lineno += 1
                    
                    if stack_lineno > 1:
                       
                        for f in F_LIST:
                            if f in line:

                                if f in f_dict:

                                    if date in f_dict[f]:
                                        f_dict[f][date][cpu] = 1
                                    else:
                                        cpu_bit_array[cpu] = 1
                                        f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                                        cpu_bit_array = VCPUS * [0]     

                                else:
                                    cpu_bit_array[cpu] = 1
                                    f_dict[f] = {}
                                    f_dict[f][date] = copy.deepcopy(cpu_bit_array)
                                    cpu_bit_array = VCPUS * [0]





            else:
                break







DATE_PATTERN = "____DATE"


def fetchval(search_list, searchline_nr, searchcolons, f, compstat):

    rec_started = False
    lineno = 0
    fetch_list = []
    fetchtxt = ""
    line = ""

    while True:

        line = f.readline()

        if line:

            if all([searchtxt in line for searchtxt in search_list]):
                rec_started = True

            if rec_started:
                lineno += 1


            if lineno == searchline_nr:
            
                parsed_line = parse(line.rstrip('\n'))

                for i, searchcol in enumerate(searchcolons):
          
                    if DATE_PATTERN in search_list:      
                        if i == (len(searchcolons) - 1):
                            fetchtxt += parsed_line[searchcol]
                        else:
                            fetchtxt += parsed_line[searchcol] + " "
                    else:
                        val = parsed_line[searchcol]
                        fetch_list.append(int(val))
                      


                if DATE_PATTERN in search_list:
                    compstat.append(fetchtxt.split('.')[0])
                else:
                    compstat += fetch_list


                break
 

        else:
            break
    
    
    return line




def stri(time):
    str_time = str(time)
    if len(str_time) == 9:
        str_time = '0' + str_time
    return str_time




def sort_time(time_dict):
    t_list = []
    for t in time_dict.iterkeys():
        t_list.append(t)

    t_list.sort()
    return t_list




def calc_diff(compstat, prev_compstat):
    cur_date = compstat[0]
    diff_compstat = [cur_date]

    for i in range(len(compstat)-1):
        diff_compstat.append("%d" % (compstat[i+1] - prev_compstat[i+1]))

    return diff_compstat
    



def log_crunch():

    compstat = []
    compstat_list = []

    prev_compstat = []


    f_time_dict = {}
    for func in F_LIST:
        t_list = sort_time(f_dict[func])
        f_time_dict[func] = copy.deepcopy(t_list)
    


    with open(COMP_LOG, 'r') as f:

        while True:

            line = fetchval([DATE_PATTERN], 2, [0], f, compstat)
            line = fetchval(["Node 0 MemFree:"], 1, [3], f, compstat, 1024)
            line = fetchval(["Node 1 MemFree:"], 1, [3], f, compstat, 1024)

            if len(compstat) == 3:
                compstat_list.append(compstat)

            compstat = []

            if not line:
                break


     
    stat_list = []


    for i in range(len(compstat_list)-1):
 
        cur_compstat = compstat_list[i]
        next_compstat = compstat_list[i+1]

        cur_time = int(cur_compstat[0][4:])
        cur_date = cur_compstat[0][:4]
        next_time = int(next_compstat[0][4:])
        next_date = next_compstat[0][:4]         


        pre_time_func_dict = {}
        mid_time_func_dict = {}
        post_time_func_dict = {}
          

        equal_time_found = False
        post_equal_time_found = False


        for func in F_LIST:
        
            for f_time in f_time_dict[func]:
            
                if i == 0:

                    if f_time < cur_time:

                        if f_time in pre_time_func_dict:
                             pre_time_func_dict[f_time].append(func)
                        else:   
                            pre_time_func_dict[f_time] = [func]
                  
                        #del f_time_dict[func][f_time]



                if i == (len(compstat_list)-2):

                    if f_time >= next_time:

                        if f_time == next_time:
                            post_equal_time_found = True


                        if f_time in post_time_func_dict:
                             post_time_func_dict[f_time].append(func)
                        else:
                            post_time_func_dict[f_time] = [func]

                        #del f_time_dict[func][f_time]

               
                if f_time >= cur_time and f_time < next_time:

                    if f_time == cur_time:
                        equal_time_found = True


                    if f_time in mid_time_func_dict:
                        mid_time_func_dict[f_time].append(func)
                    else:
                        mid_time_func_dict[f_time] = [func]      
                 
                    #del f_time_dict[func][f_time]




        if pre_time_func_dict:

             payload = len(cur_compstat[1:]) * ['0']
             t_list = sort_time(pre_time_func_dict)

             for t in t_list:
             
                bit_list = len(F_LIST) * VCPUS * [0]

                for func in pre_time_func_dict[t]:
                    func_idx = F_LIST.index(func)

                    bit_array = f_dict[func][t]
                    bit_list[VCPUS*func_idx:VCPUS*func_idx+VCPUS] = bit_array                

                stat_list.append([cur_date + stri(t)] +
                                 payload +
                                 [str(b) for b in bit_list])
                



        if not equal_time_found:      
             bit_list = len(F_LIST) * VCPUS * [0]
             stat_list.append(cur_compstat +
                              [str(b) for b in bit_list])




        if mid_time_func_dict:

             payload = cur_compstat[1:]
             t_list = sort_time(mid_time_func_dict)

             for t in t_list:

                bit_list = len(F_LIST) * VCPUS * [0]

                for func in mid_time_func_dict[t]:
                    func_idx = F_LIST.index(func)

                    bit_array = f_dict[func][t]

                    bit_list[VCPUS*func_idx:VCPUS*func_idx+VCPUS] = bit_array

                stat_list.append([cur_date + stri(t)] +
                                 payload +
                                 [str(b) for b in bit_list])




        if i == (len(compstat_list)-2):
             if not post_equal_time_found:
                 bit_list = len(F_LIST) * VCPUS * [0]
                 stat_list.append(next_compstat +
                                  [str(b) for b in bit_list])




        if post_time_func_dict:

             payload = len(next_compstat[1:]) * ['0']
             t_list = sort_time(post_time_func_dict)

             for t in t_list:

                bit_list = len(F_LIST) * VCPUS * [0]

                for func in post_time_func_dict[t]:
                    func_idx = F_LIST.index(func)

                    bit_array = f_dict[func][t]

                    bit_list[VCPUS*func_idx:VCPUS*func_idx+VCPUS] = bit_array

                stat_list.append([next_date + stri(t)] +
                                 payload +
                                 [str(b) for b in bit_list])




    with open(COMP_CSV, 'w') as f:
        for stat in stat_list:
            #print("stat %s" % stat)           
            f.write("%s\n" % ','.join(
                                      stat
                                     ))
 






def main():


    for kprobe_log in KPROBE_LOGS:
        kprobelog_crunch(kprobe_log)
    
    #stack_crunch()

    F_LIST.append("hangtimestamps")
    hangtimestamps_crunch()

    #print("DICT %s" % f_dict)

    log_crunch()




if __name__ == '__main__':
    main()


