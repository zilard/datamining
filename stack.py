#!/usr/bin/python

from datetime import datetime
import time
import subprocess
import os
import sys


STACK_CMD = "cat /proc/%s/stack | grep '%s+'"
PS_CMD = "ps --cols 60 -eTo spid,psr,command | grep %s | grep -v grep"

VIRSH_LIST_CMD = "virsh list | tail -n +3 | head -n +2"
CAT_VCPU = "cat /sys/fs/cgroup/cpuset/machine/qemu-%s-%s.libvirt-qemu/%s/tasks"
LIST_VCPUS = "ls /sys/fs/cgroup/cpuset/machine/qemu-%s-%s.libvirt-qemu | grep vcpu"

SLEEP_TIME = 0.1

QEMU_PROC_NAME = "qemu-system-x86_64"
OVS_PROC_NAME = "ovs-vswitchd"

prev_dict = {}


OVS_CORES = ["1", "21", "41", "61"]
F_LIST = ["flush_workqueue", "futex_wait_queue_me"]


vcpu_thread_list = []
vcpu_thread_cpu_dict = {}
ovs_thread_list = []
ovs_thread_cpu_dict = {}

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


def should_update(cpu, bit_array):
    if cpu not in prev_dict:
        prev_dict[cpu] = bit_array
        return True
    else:
        prev_bit_array = prev_dict[cpu]
        for i in range(len(bit_array)):
            if bit_array[i] != prev_bit_array[i]:
                prev_dict[cpu] = bit_array
                return True
    return False


def get_time():
    now = datetime.now()
    return now.strftime('%m%d%H%M%S')


def data_crunch():
  
    date = get_time()

    stat_list = []

    for thread in vcpu_thread_list:
        bit_array = stack_crunch(thread)
        cpu = vcpu_thread_cpu_dict[thread]
        if should_update(cpu, bit_array):
            stat_list.append([date, "Q", "c%s" % cpu] + [str(b) for b in bit_array])

    for thread in ovs_thread_list:
        bit_array = stack_crunch(thread)
        cpu = ovs_thread_cpu_dict[thread]
        if should_update(cpu, bit_array):
            stat_list.append([date, "D", "c%s" % cpu] + [str(b) for b in bit_array])

    return stat_list


def stack_crunch(thread_id):
    bit_array = [0] * len(F_LIST)
    for i in range(len(F_LIST)):
        r = exec_cmd(STACK_CMD % (thread_id, F_LIST[i]))
        if r:
            bit_array[i] = 1
    return bit_array


def get_vcpu_threads():
    r = parse(exec_cmd(VIRSH_LIST_CMD))
    for line in r:
        vm_id = line[0]
        vm_name = line[1]
        vcpu_list = parse(exec_cmd(LIST_VCPUS % (vm_id, vm_name)))
        for vcpu in vcpu_list:
            vcpu = vcpu[0]
            thread_list = parse(exec_cmd(CAT_VCPU % (vm_id, vm_name, vcpu)))
            for thread in thread_list:
                vcpu_thread_list.append(thread)


def map_vcpu_thread_to_cpu():
    r = parse(exec_cmd(PS_CMD % QEMU_PROC_NAME))
    for line in r:
        thread = line[0]
        if thread in vcpu_thread_list:
            cpu = line[1]
            vcpu_thread_cpu_dict[thread] = cpu


def get_ovs_threads():
    r = parse(exec_cmd(PS_CMD % OVS_PROC_NAME))
    for line in r:
        cpu = line[1]
        if cpu in OVS_CORES:
            thread = line[0]
            ovs_thread_list.append(thread)
            ovs_thread_cpu_dict[thread] = cpu
       

def main():

    STACK_CSV = "%s_stack.csv" % get_time()   
    os.mknod(STACK_CSV)

    get_vcpu_threads()
    map_vcpu_thread_to_cpu()
    get_ovs_threads()

    while True:
        stat_list = data_crunch()
        if stat_list:
            with open(STACK_CSV, 'a') as f:
                for stat in stat_list:
                    f.write("%s\n" % ','.join(stat))

        time.sleep(SLEEP_TIME)





if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

