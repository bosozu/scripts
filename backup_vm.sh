#!/bin/bash
data=`date +%d-%m-%Y`
backup_dir=/mnt/backup
vm=`sudo virsh list | grep . | awk  '{print $2}' | sed 1,2d | tr -s '\n' ' '`
for activevm in $vm
do
  sudo mkdir -p $backup_dir/$activevm

  #Backup XML configuration for current VM

  sudo virsh dumpxml $activevm > $backup_dir/$activevm/$activevm-$data.xml

  #Path current VM
  disk_path=`sudo virsh domblklist $activevm | grep vd | awk '{print $2}'`

  #Stop  current VM
  sudo virsh shutdown $activevm
  sleep 2s

  for path in $disk_path
  do
    #Create filename from path
    filename=`basename $disk_path`

    #Create backup
    gzip -c $path > /tmp/$filename-$data.gz	
    cp /tmp/$filename-$data.gz $backup_dir/$activevm/
    sleep 2s
    rm -f /tmp/$filename-$data.gz
    sleep 2s
    sudo virsh start $activevm
    sleep 2s

  done
done
/usr/bin/find /backup/ -type f -mtime +7 -exec rm -rf {} \;
