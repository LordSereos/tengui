#!/bin/bash

username="$1"
remote_host="$2"
port="$3"
shift 3

# Store the entire command as a single string
command="$*"

local_dir="./modules/runCmd/${remote_host}/"
timestamp=$(date +%m%d_%H%M)

local_dest="${local_dir}runCmd-${timestamp}.log"

mkdir -p "$local_dir"

# Echo the command into the log file
echo "$command" > "$local_dest"

# Execute the command on the remote host using eval
ssh "$username@$remote_host" "eval \"$command\"" >> "$local_dest"

