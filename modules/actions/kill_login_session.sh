#!/bin/bash

# Author: Haroldas Klangauskas
# Date:   2024-03-22

# If less than 1 parameter given -> Exit
if [[ "$#" -lt 1 ]]; then
    echo "ERROR: NOT ENOUGH PARAMETERS"
	echo "Usage: $0 [TTY]"
	echo "[TTY] - mandatory parameter, a TTY to kill"
    exit 1
fi
# If more than 1 parameter given -> Exit
if [[ "$#" -gt 1 ]]; then
    echo "ERROR: TOO MUCH PARAMETERS"
	echo "Usage: $0 [TTY]"
	echo "[TTY] - mandatory parameter, a TTY to kill"
    exit 1
fi

echo "Host: $(hostname -I)"
SCRIPT_EXECUTOR_ID=$(id -u)
echo "Running script as $(whoami) with ID: $SCRIPT_EXECUTOR_ID"
if [[ "$SCRIPT_EXECUTOR_ID" -ne 0 ]]; then
	echo "Please run $0 as root"
	echo "Exiting..."
	exit
fi

TTY_TO_KILL="$1"
pkill -KILL -et $TTY_TO_KILL
EXIT_STATUS=$?

# Make sure that kill command executed sucesfully
if [[ "$EXIT_STATUS" -ne 0 ]]; then
	echo "ERROR"
	echo "Unable to kill the session"
	echo "Exiting..."
	exit
else
	echo "TTY $TTY_TO_KILL was killed sucessfully"
fi
