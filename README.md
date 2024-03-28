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

  	- Should contain information in three columns:
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
- ...

## User interaction flow
![Alt Text](utils/Flowchart.jpg)

## Current functionality

- VIEW INDIVIDUAL HOSTS and APPLY SCRIPTS displays all hosts from the hosts file.
- User key input tracking and navigation in the menu.
- VIEW INDIVIDUAL HOSTS menu:
  - List of hosts from the host file. Navigatable and clickable, when clicked will show info about this particular host: 
    - Logged in users
    - Currently running services
  - All of the above mentioned processes are remotely terminatable - on ENTER click, a confirmation modal will appear to confirm service termination.
- APPLY SCRIPTS menu:
  - Unordered list of hosts from the host files. (TO DO: functionality to select several hosts, not only one for further actions)
  - When host(s) are selected and ENTER pressed, a window to select which scripts to apply to them opens. The scripts include:
    - CHECK PORTS: input which ports to check, or use default settings to see whether they are closed or opened and whether they should be opened, show warnings.
    - MAKE BACKUPS: backs up files from a remote host using SCP.
    - RUN LYNIS SCAN: copies files to remote. After scan returns logs which can be filtered to decide on future actions.


