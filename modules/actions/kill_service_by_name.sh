#!/bin/bash

# Author: Haroldas Klangauskas
# Date:   2024-03-22

# If less than 1 parameter given -> Exit
if [[ "$#" -lt 1 ]]; then
    echo "ERROR: NOT ENOUGH PARAMETERS"
	echo "Usage: $0 [SERVICE_NAME]"
	echo "[SERVICE_NAME] - mandatory parameter, script accepts a single service name to kill"
    exit 1
fi
# If more than 1 parameter given -> Exit
if [[ "$#" -gt 1 ]]; then
    echo "ERROR: TOO MUCH PARAMETERS"
	echo "Usage: $0 [SERVICE_NAME]"
	echo "[SERVICE_NAME] - mandatory parameter, script accepts a single service name to kill"
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

# Extract PID of the given service
EXTRACTED_PID=$(systemctl show --property MainPID $1)
# Retrieve only the PID
PID_TO_KILL="${EXTRACTED_PID#*=}"
echo "PID of service $1 $PID_TO_KILL"

# Check if such service is running
if [[ "$PID_TO_KILL" -eq 0 ]]; then
	echo "Service $1 not found"
	echo "Exiting..."
	exit
fi


kill "$PID_TO_KILL"
EXIT_STATUS=$?
# Make sure that kill command executed sucesfully
if [[ "$EXIT_STATUS" -gt 0 ]]; then
	echo "ERROR"
	echo "Unable to kill the service"
	echo "Exiting..."
	exit
fi

# Wait for service to be killed
echo "Waiting for service to be fully killed..."
sleep 2

# Retrieve the PID again and check, to make sure that the service was killed
echo "Rechecking if  service was killed"
EXTRACTED_PID=$(systemctl show --property MainPID $1)
PID_TO_KILL="${EXTRACTED_PID#*=}"
echo "PID of service $1 $PID_TO_KILL"

if [[ "$PID_TO_KILL" -eq 0 ]]; then
	echo "Service $1 killed succesfully"
else
	echo "Unknown ERROR, probably the system itself restarted $1"
	echo "Service $1 could not have been killed"
	echo "Exiting..."
	exit
fi