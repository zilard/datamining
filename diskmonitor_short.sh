SLEEP_TIME=120; \
L="/root/diskmonitor.log"; \
while true; do \
DATE="$(date +\%Y\%m\%d\%H\%M\%S)"; \
echo "____DATE" >> "${L}"; echo "${DATE}" >> "${L}"; \
echo "____DISK" >> "${L}"; \
LL="$(find /var/lib/nova/libvirt/images -name 'node[0-9].qcow')"; \
IFS=$'\n'; for D in $(echo "${LL}"); do \
S=$(ls -s "${D}" | cut -d' ' -f1); \
SH=$(ls -sh "${D}" | cut -d' ' -f1); \
echo "${D} ${SH} ${S}" >> "${L}"; \
done; \
echo "____EXTFRAG" >> "${L}"; cat /sys/kernel/debug/extfrag/extfrag_index | grep -v "DMA " >> "${L}"; \
echo "____UNUSABLE" >> "${L}"; cat /sys/kernel/debug/extfrag/unusable_index | grep -v "DMA " >> "${L}"; \
echo "____BUDDINYFO" >> "${L}"; cat /proc/buddyinfo | grep -v "DMA " >> "${L}"; \
echo "____PAGETYPEINFO" >> "${L}"; cat /proc/pagetypeinfo | grep "Node    0\|Node    1" | grep "DMA32\|Normal" | grep "Unmovable\|Movable\|Reclaimable" >> "${L}"; \
echo "____VMSTAT" >> "${L}"; cat /proc/vmstat >> "${L}"; \
echo "____FREE" >> "${L}"; free | grep "Mem:" >> "${L}"; \
echo "____MEMINFO_A" >> "${L}"; cat /proc/meminfo >> "${L}"; \
echo "____SLABINFO" >> "${L}"; cat /proc/slabinfo | grep "xfs_\|kvm_\|blkdev_\|inode_\|files_\|anon_vma\|bdev_\inode_" >> "${L}"; \
echo "____ZONEINFO" >> "${L}"; cat /proc/zoneinfo | grep "^  \|^        \|^Node\|^    \|^        " | grep -v "vm stats\|cpu:\|^              \|pagesets\|all_unreclaimable\|start_pfn\|inactive_ratio\|nr_free_cma\|protection" >> "${L}"; \
echo "____MEMINFO_NODE0" >> "${L}"; cat /sys/devices/system/node/node0/meminfo >> "${L}"; \
echo "____MEMINFO_NODE1" >> "${L}"; cat /sys/devices/system/node/node1/meminfo >> "${L}"; \
echo "____DISKSTAT" >> "${L}"; cat /proc/diskstats | grep "sdb\|dm-0" >> "${L}"; \
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@" >> "${L}"; \
sleep "${SLEEP_TIME}"; \
done

