#!/bin/bash
#

username="$1"
remote_host="$2"
port="$3"
shift 3
audit_locations=("$@")

ssh_command="sudo apt install -y auditd; sudo touch /var/log/wtmp; sudo touch /var/log/btmp; sudo apt install -y acct && sudo accton on; sudo touch /var/log/btmp; sudo chmod 600 /var/log/btmp"

ssh "$username@$remote_host" "$ssh_command"

for location in @{audit_locations[@]}; do
   ssh "$username@$remote_host" "sudo auditctl -w $location -p wa -k '${location}-FLAG'"
done
