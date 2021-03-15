


vi collect.sh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#!/bin/bash
L="/root/collect.log"; SLEEP=5; \
echo "____HOSTNAME" >> "${L}"; cat /etc/hostname >> "${L}"; \
echo "____CMDLINE" >> "${L}"; cat /proc/cmdline >> "${L}"; \
echo "____VIRSH_L" >> "${L}"; virsh list >> "${L}"; \
echo "____VIRSH_DUMPXML" >> "${L}"; \
VMS=$(virsh list | tail -n +3 | sed -e's/  */ /g' | cut -d' ' -f3 | tr '\n' ' ' | tr --delete '\n'); \
IFS=$' '; for VM in $(echo "${VMS}"); do virsh dumpxml "${VM}" >> "${L}"; done; \
while true; do \
DATE="$(date +\%Y\%m\%d\%H\%M\%S)"; \
echo "____DATE" >> "${L}"; echo "${DATE}" >> "${L}"; \
echo "____PROC_STAT" >> "${L}"; cat /proc/stat | grep "cpu\|intr" >> "${L}"; \
PS_THREADS=$(ps -eTo pid,spid,ppid,psr,class,pri,pcpu,pmem,command -w | cut -b1-160 | tail -n +2 | sort -b -k4,4n); \
echo "____PS_THREADS" >> "${L}"; echo "${PS_THREADS}" >> "${L}"; \
echo "____MPSTAT" >> "${L}"; mpstat -P ALL 10 1 | grep "Average:" >>  "${L}"; \
echo "____BUDDINYFO" >> "${L}"; cat /proc/buddyinfo >> "${L}"; \
echo "____PAGETYPEINFO" >> "${L}"; cat /proc/pagetypeinfo | grep "Node    0\|Node    1" | grep "DMA32\|Normal" | grep "Unmovable\|Movable\|Reclaimable" >> "${L}"; \
echo "____VMSTAT" >> "${L}"; cat /proc/vmstat >> "${L}"; \
echo "____FREE" >> "${L}"; free >> "${L}"; \
echo "____MEMINFO_A" >> "${L}"; cat /proc/meminfo >> "${L}"; \
echo "____ZONEINFO" >> "${L}"; cat /proc/zoneinfo | grep "^  \|^        \|^Node\|^    \|^        " | grep -v "vm stats\|cpu:\|^              " >> "${L}"; \
echo "____MEMINFO_NODE0" >> "${L}"; cat /sys/devices/system/node/node0/meminfo >> "${L}"; \
echo "____MEMINFO_NODE1" >> "${L}"; cat /sys/devices/system/node/node1/meminfo >> "${L}"; \
echo "____DISKSTAT" >> "${L}"; cat /proc/diskstats >> "${L}"; \
echo "____SAR" >> "${L}"; sar -u -P ALL -b -B -d -R -r -w -n DEV -p -S 10 1 | grep "Average:" >> "${L}"; \
sleep "${SLEEP}"; \
done;
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
chmod +x collect.sh
 
nohup ./collect.sh &

