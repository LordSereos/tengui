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
- tengui.py - script which initializes the terminal user interface.

## Usage
```bash
python3 tengui.py
```
### Prerequisites:
- python3
- ssh keys exchange between monitoring machine and other hosts
- ...

## Current functionality

- Main menu displays all hosts from the hosts file
- User key input tracking and navigation in the main menu
- Functionality to click on a host from main menu and view information about it:
  - Logged in users
  - Currently running services
- Navigating through the selected host information window
