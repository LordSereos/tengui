#!/bin/bash
#

message "$1" "$2"
ssh "$2" 'sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
          sudo tee /etc/apt/sources.list >/dev/null' <<EOF
            deb http://deb.debian.org/debian/ stable main contrib non-free
            deb-src http://deb.debian.org/debian/ stable main contrib non-free

            deb http://deb.debian.org/debian/ stable-updates main contrib non-free
            deb-src http://deb.debian.org/debian/ stable-updates main contrib non-free

            deb http://deb.debian.org/debian-security stable/updates main
            deb-src http://deb.debian.org/debian-security stable/updates main

            deb http://ftp.debian.org/debian buster-backports main
            deb-src http://ftp.debian.org/debian buster-backports main
            EOF

ssh "$2" 'if ! command -v python3 &> /dev/null; then \
         sudo apt update && \
         sudo apt install -y python3 && \
         echo "Python 3 installed successfully"; \
         else \
         sudo apt update &&
         echo "Python 3 is already installed"; \
         fi'

