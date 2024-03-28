#!/bin/bash
#

if [ $# -lt 3 ]; then
    echo "Not enough args"
    exit 1
fi

username="$1"
remote_host="$2"
port="$3"
local_directory="./reports/${remote_host}"

scp -P "$port" ./lynis-remote.tar.gz "${username}@${remote_host}:~/"

ssh -T -q -p ${port} "${username}@${remote_host}" <<EOF
mkdir -p ~/tmp-lynis &&
cd ~/tmp-lynis &&
tar xzf ../lynis-remote.tar.gz &&
rm ../lynis-remote.tar.gz &&
cd lynis &&
./lynis audit system > /dev/null
EOF

ssh -p ${port} "${username}@${remote_host}" "rm -rf ~/tmp-lynis"

mkdir -p ${local_directory}
scp -q -P ${port} "${username}@${remote_host}:~/lynis.log" ${local_directory}
scp -q -P ${port} "${username}@${remote_host}:~/lynis-report.dat" ${local_directory}

echo "Completed."

