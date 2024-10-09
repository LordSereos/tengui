# Tengui

## Introduction

Name "Tengui" is composed of two expressions: *Tengu* + *UI* 

**Tengu** are mythical bird-like creatures in Japanese culture, protectors of nature and skilled warriors. Just like them, our application will watch over "green" systems and act viciously to protect them.

Tengui TUI (terminal user interface) is a work-in-progress tool for remote host observation and management made by Vilnius University faculty of Mathematics and Informatics Information Technologies students:

- Martin Martijan (LordSereos)
- Tomas Petruoka (tmsptr)
- Haroldas Klangauskas (HaroldasKL)

Under supervision of:

- dr. Linas Bukauskas
- lect. Virgilijus Krinickij

Aim of this tool is to quickly display necessary monitoring information about connected hosts machines (Linux only) and provide functionality to quickly mitigate possible threats, which can be deducted from the displayed information in the TUI.

## Contents
There are following directories and files in this project:

- Modules - folder containing necessary scripts for updating and managing hosts.
- hosts - file which should be populated with IPv4 addresses of hosts for desired monitoring.
    - Write group name for the hosts below (for example WEBSERVERS)
  	- Then write information in three columns:
  	  **{IP} {port} {username}**
  	- Example could be: **10.0.0.1 2222 root**

- tengui.py - script which initializes the terminal user interface.

## Usage
```bash
python3 tengui.py
```
### Prerequisites:
- python3
- ssh keys exchange between monitoring machine and other hosts
- user must have root privileges on the remote host
- local_dir in modules/* scripts has to be changed to the local directory of the using machine. Now it is set to /home/sereos/Desktop/..., but all of these instances has to be changed for user which runs the TUI. (TO DO: have a separate file where we would need to change that only once, and then scripts would read the path from that file)
- terminal height should be not smaller than 22 lines. Some of the parts are not scrollable, WIP.

## User interaction flow
![Alt Text](utils/Flowchart.jpg)

## Current functionality

- Hosts can be grouped. If there are just a couple of them, add them under the first group and don't create more. Scrolling isn't yet implemented for hosts view.
- VIEW INDIVIDUAL HOSTS menu:
  - List of hosts from the host file. Navigatable and clickable, when clicked will show info about this particular host: 
    - Logged in users
    - Currently running services
    - Opened ports
  - All of the above mentioned processes are remotely terminatable (except for ports) - on ENTER click, a confirmation modal will appear to confirm service termination.
  - Context menu can be opened with 'h' for advanced navigation in the menu.
- APPLY SCRIPTS menu:
  - One, multiple or all hosts in the host group can be selected to further apply scripts to them.
  - When host(s) are selected and ENTER pressed, a window to select which scripts to apply to them opens. The scripts include:
    - CHECK PORTS: input which ports to check, or use default settings to see whether they are closed or opened and whether they should be opened, show warnings. Output is shown in **tengui/** directrly (TO DO: change it to /tengui/modules/ports)
    - MAKE BACKUPS: backs up files from a remote host using SCP. Backed up directories are found in **Tengui/backups**.
    - RUN LYNIS SCAN: returns logs to **tengui/modules/lynisCan**.
    - MANIFEST: creates MD5 hashes and runs diff with the previous hash ouput, per location. Diff output in **tengui/modules/hasher**.
  NOTES:
There have to be two hash files present locally for differ to work on.
Filenames include timestamp therefore files created within the same minute window overwrite.
    - CHECK ROOTKIT: runs rootkit/backdoor checks remotely. Saves output in **tengui/modules/chkrootkit**. Give few minutes for all scripts to execute and log to appear.
    - AUDIT SETUP: prepares remote host agents for audit retrieval script.
    - AUDIT RETRIEVAL: retrieves last, lastb, lastlog, ac, lastcomm logs from remote machine, stores locally in **tengui/modules/audit** for inspection and forensics.
    - CUSTOM COMMAND: any one-liner command can be entered to be executed on the remote host(s). If applicable, output will be shown in **/tengui/modules/runCmd**
  - Scripts are run simultaneously on multiple hosts, and some of them (like Lynis Scan) are run on the background.


