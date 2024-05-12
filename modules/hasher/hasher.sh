#!/bin/bash
#
#HASH ALL -> SEND HOME -> GET RID OF EVIDENCE

hash_locations=("$@")
local_dir="./hashes/"
timestamp=$(date +%m%d_%H%M)

remote_user=tom
remote_port=22
remote_host=192.168.1.188
local_host=$(ip route get 1.2.3.4 | awk '{print $7}')
remote_dest="/home/tom/incoming/${local_host}/"

mkdir -p "$local_dir"

for path in "${hash_locations[@]}"; do
   file_list=()
    
   while IFS= read -r file; do
      file_list+=("$file")
   done < <(find "$path" -type f)
   
   for file in "${file_list[@]}"; do
      filename=$(echo "$file" | tr '/' '_')
      local_dest="${local_dir}${filename}-${timestamp}.hash"
      hash=$(md5sum "$file" | awk '{print $1}')
      echo "$hash" > "${local_dest}"
   done
done

tar_file=hashes_${timestamp}.tar
tar cvf ${tar_file} ./hashes/
rsync -e "ssh -p ${remote_port}" ${tar_file} ${remote_user}@${remote_host}:${remote_dest}

rm -rf ${local_dir}
rm -f ${tar_file}