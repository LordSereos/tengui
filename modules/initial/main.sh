#!/bin/bash

apt_script="./configs/apt.sh"
pacman_script="./configs/pacman.sh"

####################################################################################
#########                                                                  
#########    Package manager identification                                                            
#########                                                               
####################################################################################

declare -A osInfo
osInfo[/etc/redhat-release]=yum
osInfo[/etc/arch-release]=pacman
osInfo[/etc/SuSE-release]=zypp
osInfo[/etc/debian_version]=apt
osInfo[/etc/alpine-release]=apk

determine_distro() {
   local PKGMANAGER=""
   for file in ${!osInfo[@]}; do
      if [[ -f $file ]]; then
         PKGMANAGER=${osInfo[$file]}
         break
      fi
   done
   echo "$PKGMANAGER"
}

####################################################################################
#########                                                                  
#########    Updating package manager mirrors and setting up python                                                           
#########    via external scripts
#########
####################################################################################

message() {
   echo "Updating $1 and PYTHON3 on $2"
}

update() {
    if [[ "$1" = "apt" ]]; then
       source "$apt_script" "$1" "$2"
    elif [[ "$1" = "pacman" ]]; then
       source "$pacman_script" "$1" "$2"
    fi
}

main() {
   local PKGMANAGER=""
   PKGMANAGER=$(determine_distro)
   [[ -z "$PKGMANAGER" ]] && echo "Unable to get package manager" && exit 1
   
#   for host in "$@"; do
#      if ssh -q "$host" exit; then
#         update "$PKGMANAGER" "$host"
#      else
#         echo "Failed connection to "$host""
#      fi
#   done

   update "$PKGMANAGER" "$HOSTNAME"
}

main

