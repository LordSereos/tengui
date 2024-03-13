#!/bin/bash
#

get_process_info() {
    local port="$1"
    local output_file="$2"
    local ssh_user="$3"
    local ssh_host="$4"

    sudo ssh "$ssh_user@$ssh_host" "lsof -i :$port" > "$output_file"
}

close_port() {
    local port="$1"
    local iptables_fil="$2"
    local ssh_user="$3"
    local ssh_host="$4"

    sudo iptables-save > "$iptables_file"
    sudo ssh "$ssh_user@$ssh_host" "sudo iptables -A INPUT -p tcp --dport $port -j DROP"
    sudo iptables-save > /etc/iptables/rules.v4
}

####################################################################################
#########                                                                  
#########    Create scripts for automatically loading iptables rules on boot!!!                                                       
#########
####################################################################################

main() {
    local ssh_user="$1"
    local ssh_host="$2"
    shift 2
    local ports_to_close=("$@")
    local output_directory="./$ssh_host_closedPortsInfo"

    mkdir -p "$output_directory"

    for port in "${ports_to_close[@]}"; do
        port_file="$output_directory/process_info_port_$port.txt"
        iptables_file="$output_directory/iptables_info.txt"
        get_process_info "$port" "$output_file" "$ssh_user" "$ssh_host"
        close_port "$port" "$iptables_file" "$ssh_user" "$ssh_host"
    done
}

main
