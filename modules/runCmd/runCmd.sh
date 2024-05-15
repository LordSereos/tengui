#!/bin/bash

username="$1"
remote_host="$2"
port="$3"
shift 3
command=("$@")
local_dir="/home/tom/MEGA/treciasKursas/tengui/modules/chrootkit/${remote_host}/"
timestamp=$(date +%m%d_%H%M)

#local_dest="${local_dir}$runCmd.log"
local_dest="${local_dir}$runCmd-${timestamp}.log"

mkdir -p "$local_dir"

#ssh "$username@$remote_host" "$command" >> "$local_dest"
ssh "$username@$remote_host" "$command" > "$local_dest"