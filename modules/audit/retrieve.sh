#!/bin/bash
#

username="$1"
remote_host="$2"
port="$3"
shift 3
audit_locations=("$@")
local_dir="/home/sereos/Desktop/tengui/modules/audit/${remote_host}/"
timestamp=$(date +%m%d_%H%M)

mkdir -p "$local_dir"

ssh "$username@$remote_host" "last" >> "${local_dir}last-${timestamp}.log"
ssh "$username@$remote_host" "lastb" >> "${local_dir}lastb-${timestamp}.log"
ssh "$username@$remote_host" "lastlog" >> "${local_dir}lastlog-${timestamp}.log"
ssh "$username@$remote_host" "ac -p" >> "${local_dir}ac-${timestamp}.log"
ssh "$username@$remote_host" "lastcomm" >> "${local_dir}lastcomm-${timestamp}.log"

for location in ${audit_locations[@]}; do
   ssh "$username@$remote_host" "ausearch -k ${location}-FLAG" >> "${local_dir}ausearch-${location}-${timestamp}.log"
done
