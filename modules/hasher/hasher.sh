#!/bin/bash

username="$1"
remote_host="$2"
port="$3"
shift 3
hash_locations=("$@")
local_dir="/home/tom/MEGA/treciasKursas/tengui/modules/hasher/${remote_host}/"
timestamp=$(date +%m%d_%H%M)
changelog="${local_dir}changelog"

mkdir -p "$local_dir"
touch $changelog

for location in "${hash_locations[@]}"; do
    loc_edit=$(echo "$location" | sed 's/\//_/g')
    local_dest="${local_dir}${loc_edit}-${timestamp}.hashes"
    touch "$local_dest"

    ssh_command="sudo find \"$location\" -type f | xargs sudo md5sum | awk '{print \$2 \" - \" \$1}'"
    ssh "$username@$remote_host" "$ssh_command" >> "$local_dest"

    hash_files=($(find "$local_dir" -maxdepth 1 -type f -name "${loc_edit}*.hashes"))
    num_files=${#hash_files[@]}

    if [ $num_files -gt 2 ]; then
        oldest_file=${hash_files[0]}
        oldest_timestamp=$(basename "$oldest_file" | grep -oP '\d{4}_\d{4}' | sed 's/_//')
        
        for hash_file in "${hash_files[@]}"; do
            current_timestamp=$(basename "$hash_file" | grep -oP '\d{4}_\d{4}' | sed 's/_//')
            if [ "$current_timestamp" -lt "$oldest_timestamp" ]; then
                oldest_timestamp="$current_timestamp"
                oldest_file="$hash_file"
            fi
        done
        rm $oldest_file

        diff_files=()

        for hash_file in ${local_dir}${loc_edit}*.hashes; do
            diff_files+=("$hash_file")
        done

        diff_output=$(diff -c "${diff_files[0]}" "${diff_files[1]}")
        echo "$diff_output" >> $changelog
    fi
done








