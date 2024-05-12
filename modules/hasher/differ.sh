#!/bin/bash
#
#CHECK AND REPORT

tar_file="$1"
working_dir="$2"
newest_timestamp="$3"

prefix=$(echo ${tar_file} | cut -d "@" -f1)
cd $working_dir
touch changelog
tar_files=$(find . -maxdepth 1 -type f -name "${prefix}*.tar")
num_files=$(echo "$tar_files" | wc -l)

if [ "$num_files" -gt 2 ]; then
   oldest_file=$(echo "$tar_files" | xargs stat --format="%Y %n" | sort -n | head -n 1 | awk '{print $2}')
   rm "$oldest_file"
   oldest_dir=${oldest_file%.tar}
   rm -rf $oldest_dir

   for file in "${prefix}"*.tar; do
      base_name="${file%.tar}"
      mkdir -p "$base_name"
      extracted_dirs+=("$base_name")
      tar xvf "$file" -C "${file%.tar}"
   done

   diff_output=$(diff -rq "${extracted_dirs[0]}" "${extracted_dirs[1]}")
   echo "$diff_output" >> changelog
fi

