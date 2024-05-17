#!/bin/bash
#
username="$1"
remote_host="$2"
port="$3"
shift 3
audit_locations=("$@")

ssh_command="sudo touch /var/log/wtmp; sudo touch /var/log/btmp; sudo apt install -y acct && sudo accton on"
#ssh_command="curl -O https://ftp.gnu.org/gnu/acct/acct-6.6.4.tar.gz"         IF NOT IN REPO   
#scp acct-6.6.4.tar.gz $username@$remote_host:/home/$username                 PUSH IF NEEDED
#ssh_command="cd /home/$username && tar xf acct-6.6.4.tar.gz && cd acct-6.6.4 && ./configure && sudo make install"

ssh "$username@$remote_host" "$ssh_command"

for location in @{audit_locations[@]}; do
   ssh "$username@$remote_host" "sudo auditctl -w $location -p wa -k '${location}-FLAG'"
done
