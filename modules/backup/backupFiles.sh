#!/bin/bash
#

if [ $# -lt 4 ]; then
    echo "Not enough args"
    exit 1
fi

username="$1"
remote_host="$2"
port="$3"
shift 3 
copy_locations=("$@")

timestamp=$(date +%m%d_%H%M)

for path in "${copy_locations[@]}"; do
    filename=$(basename "$path")
    local_directory="./backups/${remote_host}"
    local_destination="./backups/${remote_host}/${filename}-${timestamp}"
    if [ ! -d ${local_directory} ]; then
       mkdir -p "$local_directory"
    fi
    scp -r -P "$port" "${username}@${remote_host}:${path}" "$local_destination"
    if [ $? -ne 0 ]; then
        echo "Failed"
    fi
done


