#!/bin/bash

username="$1"
remote_host="$2"
port="$3"
shift 3
hash_locations=("$@")
local_dir="/home/tom/MEGA/treciasKursas/tengui/modules/chrootkit/${remote_host}/"
local_dest="${local_dir}$chkrootkit-${timestamp}.log"
timestamp=$(date +%m%d_%H%M)
changelog="${local_dir}changelog"

mkdir -p "$local_dir"
touch $changelog

ssh "$username@$remote_host" "sudo apt install gcc"
scp chkrootkit.tar.gz $username@$remote_host:/home/$username
ssh_command="cd /home/$username && tar xvf chkrootkit.tar.gz && cd chkrootkit-0.58b && sudo make sense && sudo ./chkrootkit"
ssh "$username@$remote_host" "$ssh_command" >> "$local_dest"









