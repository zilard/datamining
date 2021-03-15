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

VM_FILE = "collect_20210216_084220.log"
PROCSTAT_CSV = "compute_procstat_084220.csv"

CPU_LIST = ['26', '33', '66', '73']



def ll_sp_value(value1, value2, itv):
    if ((value2 < value1) and (int(value1) <= 0xffffffff)):
        return (float(int(value2 - value1) & 0xffffffff) / itv) * 100
    else:
        return ((value2 - value1) / itv) * 100



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
    procstat_maxline = 82

    date = ""

    procstat_dict = {}

    prev_date = ""


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
                  


                if procstat_start in line:
                    procstat_rec_started = True

                    if prev_date:
                        procstat = [prev_date]
                    prev_date = date

            
                if procstat_rec_started:
                    procstat_lineno += 1

                    if procstat_lineno > 2:

                        c_procstat_line = parse(line.rstrip('\n'))

                        cpu = c_procstat_line[0].lstrip("cpu")

                        if cpu in CPU_LIST:

                            if cpu in procstat_dict:
                                  
                                p_procstat_line = procstat_dict[cpu]

                                c_user = float(c_procstat_line[1])
                                c_nice = float(c_procstat_line[2])
                                c_system = float(c_procstat_line[3])
                                c_idle = float(c_procstat_line[4])
                                c_iowait = float(c_procstat_line[5])
                                c_hardirq = float(c_procstat_line[6])
                                c_softirq = float(c_procstat_line[7])
                                c_steal = float(c_procstat_line[8])
                                c_guest = float(c_procstat_line[9])
                                c_guest_nice = float(c_procstat_line[10])

                                p_user = float(p_procstat_line[1])
                                p_nice = float(p_procstat_line[2])
                                p_system = float(p_procstat_line[3])
                                p_idle = float(p_procstat_line[4])
                                p_iowait = float(p_procstat_line[5])
                                p_hardirq = float(p_procstat_line[6])
                                p_softirq = float(p_procstat_line[7])
                                p_steal = float(p_procstat_line[8])
                                p_guest = float(p_procstat_line[9])
                                p_guest_nice = float(p_procstat_line[10])

                                procstat_dict[cpu] = c_procstat_line                              


                                ishift = 0.0

                                if ((c_user - c_guest) < (p_user - p_guest)):
                                    ishift += ((p_user - p_guest) - (c_user - c_guest))

                                if ((c_nice - c_guest_nice) < (p_nice - p_guest_nice)):
                                    ishift += ((p_nice - p_guest_nice) - (c_nice - c_guest_nice))



                                   
                                interval = ((c_user + c_nice +
                                             c_system + c_iowait +
                                             c_idle + c_steal +
                                             c_hardirq + c_softirq) -
                                            (p_user + p_nice +
                                             p_system + p_iowait +
                                             p_idle + p_steal +
                                             p_hardirq + p_softirq) +
                                             ishift)         
 
                                
                                user = "%.2f" % (0.0 if ((c_user - c_guest) < (p_user - p_guest)) else ll_sp_value((p_user - p_guest), (c_user - c_guest), interval))
                                #user = "%.2f" % ll_sp_value(p_user, c_user, interval)

                                nice = "%.2f" % (0.0 if ((c_nice - c_guest_nice) < (p_nice - p_guest_nice)) else ll_sp_value((p_nice - p_guest_nice), (c_nice - c_guest_nice), interval))
                                #nice = "%.2f" % ll_sp_value(p_nice, c_nice, interval)                                

                                system = "%.2f" % ll_sp_value(p_system, c_system, interval)
                                
                                iowait = "%.2f" % ll_sp_value(p_iowait, c_iowait, interval)

                                hardirq = "%.2f" % ll_sp_value(p_hardirq, c_hardirq, interval)
                                
                                softirq = "%.2f" % ll_sp_value(p_softirq, c_softirq, interval)
                
                                guest = "%.2f" % ll_sp_value(p_guest, c_guest, interval)

                                guest_nice = "%.2f" % ll_sp_value(p_guest_nice, c_guest_nice, interval)

                                procstat = procstat + [user, nice, system, iowait, hardirq, softirq, guest, guest_nice]
                                #procstat = procstat + [user, nice, system, iowait]



                                """
                                interval = (
                                            (
                                             c_user + c_nice +
                                             c_system + c_iowait +
                                             c_idle + c_steal +
                                             c_hardirq + c_softirq
                                            ) -
                                            (
                                             p_user + p_nice +
                                             p_system + p_iowait +
                                             p_idle + p_steal +
                                             p_hardirq + p_softirq
                                            ) +
                                            ishift
                                           )         
 
                                #system = "%.2f" % (((c_system - p_system) / interval) * 100)
                                system = "%.2f" % ll_sp_value(p_system, c_system, interval)

                                procstat += [system]
                                """

                            else:
 
                                procstat_dict[cpu] = c_procstat_line



                        if procstat_lineno == procstat_maxline:
                            procstat_rec_started = False
                            procstat_lineno = 0
                            if procstat:
                                procstat_list.append(procstat)
                            procstat = []

            else:
                break


    i = 0
    with open(PROCSTAT_CSV, 'w') as f:
        for procstat in procstat_list:
            #i = procstat_list.index(procstat)
            #print("___i %s" % i)
            #print("%s\n" % procstat)
            
            f.write("%s\n" % ','.join(
                                      [ 
                                        str(i) 
                                      ] +
                                      procstat
                                     ))
            i += 1
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()


