#!/bin/bash

username="$1"
remote_host="$2"
port="$3"
shift 3
command=("$@")
local_dir="/home/tom/MEGA/treciasKursas/tengui/modules/chrootkit/${remote_host}/"
timestamp=$(date +%m%d_%H%M)

#CREATE ONE OUTPUT FILE ONLY
#local_dest="${local_dir}$runCmd.log"
#CREATE NEW FILE FOR EVERY OUTPUT
local_dest="${local_dir}$runCmd-${timestamp}.log"

mkdir -p "$local_dir"

#APPEND TO ONE LOG PER HOST
#ssh "$username@$remote_host" "$command" >> "$local_dest"
#CREATE NEW TIMESTAMPED LOG
ssh "$username@$remote_host" "$command" > "$local_dest"