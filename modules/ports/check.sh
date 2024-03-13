#!/bin/bash
#

allowed_ports=("$@")

LSOF_OUTPUT=$(sudo lsof -i -P -n)
echo "$LSOF_OUTPUT"

####################################################################################
#########                                                                  
#########    Checking for ports which should not be open                                                           
#########                                                               
####################################################################################

while read -r line; do
    NAME=$(echo "$line" | awk '{print $9}')
    MODE=$(echo "$line" | awk '{print $10}')
    PORT=$(echo "$NAME" | awk -F: '{print $NF}')
    CONNECTION_MODE=$(echo "$MODE" | awk -F '[()]' '{print $2}')
    
    if [[ "$CONNECTION_MODE" == "LISTEN" ]] && [[ ! "${allowed_ports[@]}" =~ "${PORT}" ]]; then
        echo "WARNING: THIS SHOULD BE CLOSED --> $line"
    fi
done <<< "$LSOF_OUTPUT"

####################################################################################
#########                                                                  
#########    Checking for ports which should be open                                                            
#########                                                               
####################################################################################

for port in "${allowed_ports[@]}"; do
    if ! grep -q ":$port " <<< "$LSOF_OUTPUT"; then
        echo "WARNING: PORT $port IS NOT LISTENING"
    fi
done
