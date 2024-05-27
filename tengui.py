import curses
import subprocess
import paramiko
import functions
import concurrent.futures

def main(stdscr):

    ###################################################################
    ### Setting up TUI:
    ### curs_set(0) disables the cursor.
    ###################################################################
    
    curses.curs_set(0)
    
    ###################################################################
    ### ASCII art title, will be used in several windows.
    ###
    ### Might add a check if terminal dimensions are small, instead of
    ### showing a full scale title show smaller version or don't show
    ### at all.
    ###################################################################
    h, w = stdscr.getmaxyx()

    title = [
    "___________                         .__",
    "\\__    ___/___   ____    ____  __ __|__|",
    "  |    |_/ __ \\ /    \\  / ___\\|  |  \\  |",
    "  |    |\\  ___/|   |  \\/ /_/  >  |  /  |",
    "  |____| \\___  >___|  /\\___  /|____/|__|",
    "             \\/     \\//_____/           "
    ]
    if h > 21 and w > 30:
        title2 = [
            "░███████████                     ░████  ░███░████ ",
            "░   ░███  ██████ ████████   ██████░███   ░██ ░███ ",
            "    ░███ ███░███░░███░░███ ███░░██░███   ░██ ░███ ",
            "    ░███░███░░░  ░███ ░███░███ ░██░███   ░██ ░███ ",
            "    ████░░██████ ████ ████░░██████░█████████ ░███",
            "   ░░░░░ ░░░░░░ ░░░░ ░░░░░ ░░░░░██░░░░░░░░░░  ░░░ ",
            "                            ██████                "
        ]
    else:
        title2 = [
            "TengUI"
        ]
    
    display_menu(stdscr, title2)
       
def display_menu(stdscr, title):

    ###################################################################
    ### display_menu() - starting menu where user can select whether
    ### he wants to view some host information (VIEW INDIVIDUAL HOSTS),
    ### or apply scripts to one or several hosts (APPLY SCRIPTS).
    ###################################################################
    
    ###################################################################
    ### Get parameters of opened tab of the terminal.
    ### Used for displaying information dynamically according to the
    ### size of the window. Title will always be displayed in the top
    ### middle of each menu screen.
    ###
    ### TO DO: If terminal dimension are small, don't show title.
    ###################################################################
    
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2   

    ###################################################################
    ### selected_row is used to track on which line user currently is.
    ###################################################################
    
    selected_row = 0
      
    ###################################################################
    ### Read from hosts file to retrieve desired hosts.
    ### 'hosts' file should be in the same directory as this script.
    ###
    ### hosts     - an array for host IP addresses.
    ### ports     - an array for host ssh port number.
    ### usernames - an array for host connection usernames.
    ###################################################################
    
    hosts = []
    ports = []
    usernames = []

    with open('hosts', 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) >= 2:
                ip_address = parts[0]
                port = parts[1]
                username = parts[2]
                hosts.append(ip_address)
                ports.append(port)
                usernames.append(username)
    
    ###################################################################
    ### Main menu options which can be selected by clicking ENTER for
    ### further action and navigation.
    ###################################################################
    
    menu_options = ["VIEW INDIVIDUAL HOSTS", "APPLY SCRIPTS"]
    
    ###################################################################
    ### Infinite loop is used to constantly record user interaction
    ### with the terminal and update showing information, which is 
    ### userful for highlighting the row on which user currently is.
    ###################################################################
    
    while True:
        
        ###################################################################
        ### Adds title and menu options to display on the screen.
        ### Highlights currently selected menu option with curses.A_REVERSE
        ### font with the help of current_row which changes every time
        ### user moves UP or DOWN.
        ###
        ### Initializing main color theme of yellow+black for title and
        ### information boxes.
        ###################################################################

        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        for i, line in enumerate(title):
            stdscr.addstr(title_y + i, title_x, line, curses.color_pair(1))

        ###################################################################
        ### Adding border to the main menu options for better visual
        ### effect. We need to draw 2 horizontal and 2 vertical lines
        ### (vline and hline) around the area where options will be
        ### displayed. .addch are corners for the box.
        ###
        ### box_start_y - top-left box corner on the y-axis.
        ### box_end_y   - bottom-left box corner on the y-axis.
        ### box_start_x - top-left box corner on the x-axis.
        ### box_end_x   - right box corners on the x-axis.
        ###
        ### .attron()   - enables color theme for all text and lines.
        ### .attroff()  - disables color theme from this line on.
        ###################################################################

        box_start_y = title_y + len(title) + 2
        box_end_y = box_start_y + len(menu_options) + 3
        box_start_x = (w - (2 * w // 3)) // 2  # (Centered horizontally)
        box_end_x = 2 * w // 3

        stdscr.attron(curses.color_pair(1))
        stdscr.hline(box_start_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.hline(box_end_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.vline(box_start_y + 1, box_start_x, curses.ACS_VLINE, box_end_y - box_start_y - 1)
        stdscr.vline(box_start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE,
                     box_end_y - box_start_y - 1)

        stdscr.addch(box_start_y, box_start_x, curses.ACS_ULCORNER)
        stdscr.addch(box_start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
        stdscr.addch(box_end_y, box_start_x, curses.ACS_LLCORNER)
        stdscr.addch(box_end_y, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

        header_text = "Main menu"
        header_x = box_start_x + 2
        stdscr.addstr(box_start_y, header_x, header_text, curses.A_ITALIC | curses.color_pair(1))
        stdscr.attroff(curses.color_pair(1))

        ###################################################################
        ### Show the menu options inside the box.
        ### We want contents to be centered and have margins from the box
        ### lines.
        ###################################################################
        for i, option in enumerate(menu_options):
            x = box_start_x + ((2 * w // 3) - len(option)) // 2  # (Centered horizontally)
            y = box_start_y + i + 2

            if i == selected_row:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)

        ###################################################################
        ### footer_message is used as a footer which will always be
        ### displayed at the bottom of the screen. Reminds user of useful
        ### commands or how to open context menu (if applicable).
        ###################################################################
        
        footer_message = f"Press 'q' to exit"
        stdscr.addstr(h-2, 1, footer_message, curses.A_DIM | curses.A_ITALIC)
        
        ###################################################################
        ### User input capturing using keyboard:
        ###
        ### Keyboard keys UP and DOWN manage selected_row.
        ### Enter - enforces action on the current line (selected_row).
        ###         Depending on which option is selected, different menu
        ###         will be opened next.
        ### q     - used to go back or quit the TUI.
        ###
        ### max parameter ensures if selected_row is 0, it cannot decrement
        ### to a negative value and user will stay on the top-most element
        ### in the option menu.
        ###
        ### min parameter similarly doesn't allow to select more elements
        ### than there are in the menu options. It will stop at the last 
        ### element in the array of selectable items.
        ###
        ### stdscr.clear() clears the screen before displaying everything
        ### again using stdscr.refresh(). Used for cases to fix Python 
        ### curses feature that text can be displayed on top of other text,
        ### and if some text was longer than previously, when displaying
        ### new shorter text that longer part would still be displayed,
        ### because shorter text does not overlap it.
        ###################################################################
        
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_row == 0:
                isReadOnly = True
            else:
                isReadOnly = False
            display_hosts_groups(stdscr, title, isReadOnly)
        elif key == ord('q'):
            break
        stdscr.clear()
        stdscr.refresh()
    
def display_hosts_groups(stdscr, title, isReadOnly):

    ###################################################################
    ### display_hosts_groups() - secondary menu where user can view
    ### the group names and select one to see the hosts which are in
    ### that group.
    ##################################################################

    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2
    
    selected_row = 0

    ###################################################################
    ### Read from hosts file and determine groups and their hosts.
    ###
    ### groups['name']  - all names of the groups from hosts file.
    ### groups['hosts'] - all hosts of particular groups['name'].
    ###################################################################

    groups = []
    current_group = None

    with open('hosts', 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces
            if line.startswith("-"):
                if current_group is not None:
                    groups.append(current_group)
                current_group = {'name': line[1:], 'hosts': []}
            elif line:  # If the line is not empty
                current_group['hosts'].append(line)

        if current_group is not None:
            groups.append(current_group)



    # selected_hosts = set()

    while True:

        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        for i, line in enumerate(title):
                stdscr.addstr(title_y + i, title_x, line, curses.color_pair(1))
                
        ###################################################################
        ### Menu items are host group names from the hosts file.
        ###################################################################
        box_start_y = title_y + len(title) + 2
        box_end_y = box_start_y + len(groups) + 3
        box_start_x = (w - (2 * w // 3)) // 2  # (Centered horizontally)
        box_end_x = 2 * w // 3

        stdscr.attron(curses.color_pair(1))
        stdscr.hline(box_start_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.hline(box_end_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.vline(box_start_y + 1, box_start_x, curses.ACS_VLINE, box_end_y - box_start_y - 1)
        stdscr.vline(box_start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE,
                     box_end_y - box_start_y - 1)

        stdscr.addch(box_start_y, box_start_x, curses.ACS_ULCORNER)
        stdscr.addch(box_start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
        stdscr.addch(box_end_y, box_start_x, curses.ACS_LLCORNER)
        stdscr.addch(box_end_y, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

        if (isReadOnly):
            header_text = "View hosts"
        else:
            header_text = "Apply scripts"

        header_x = box_start_x + 2
        stdscr.addstr(box_start_y, header_x, header_text, curses.A_ITALIC | curses.color_pair(1))
        stdscr.attroff(curses.color_pair(1))


        for i, group in enumerate(groups):
            y = box_start_y + i + 2
            x = box_start_x + ((2 * w // 3) - len(group['name'])) // 2

            if i == selected_row:
                stdscr.addstr(y, x, group['name'], curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, group['name'])

            y += 1
                 
        footer_message = f"Press 'q' to go back to the main menu"
        stdscr.addstr(h-2, 1, footer_message, curses.A_DIM | curses.A_ITALIC)
        
        ###################################################################
        ### When group is selected (ENTER is pressed), a new window will
        ### be displayed with all hosts of that group.
        ################################################################### 
         
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(groups) - 1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            display_host_group_hosts(stdscr, groups[selected_row], title, isReadOnly)
        elif key == ord('q'):
            break

        stdscr.clear()
        stdscr.refresh()

def display_host_group_hosts(stdscr, group, title, isReadOnly):

    ###################################################################
    ### display_host_group_hosts() - submenu where user can select a
    ### host from the chosen group for further inspection.
    ###################################################################

    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2

    selected_row = 0

    ###################################################################
    ### From the lines of the group host extract explicitly host IP,
    ### ssh port and username.
    ###################################################################

    hosts_ips = []
    hosts_ports = []
    hosts_usernames = []

    for host in group['hosts']:
        parts = host.split()
        ip_address = parts[0]
        port = parts[1]
        username = parts[2]
        hosts_ips.append(ip_address)
        hosts_ports.append(port)
        hosts_usernames.append(username)

    ###################################################################
    ### Using set to store unique host elements from hosts[] list and
    ### use quick functions like .add and .remove to modify the set.
    ###################################################################

    selected_hosts = set()

    ###################################################################
    ### Initialize different colour pairings to distinguish selected
    ### hosts from unselected and currently standing line.
    ###
    ### GREEN text on BLACK background - currently selected line, which
    ### is reverse of pair 2 (curses.A_REVERSE).
    ### GREEN text OR GREEN background - means that host is in the
    ### set of selected hosts.
    ###################################################################

    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Selected host
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Non-selected host

    while True:

        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        for i, line in enumerate(title):
            stdscr.addstr(title_y + i, title_x, line, curses.color_pair(1))

        ###################################################################
        ### Menu items are host group names from the hosts file.
        ###################################################################

        box_start_y = title_y + len(title) + 2
        box_end_y = box_start_y + len(hosts_ips) + 3
        box_start_x = (w - (2 * w // 3)) // 2  # (Centered horizontally)
        box_end_x = 2 * w // 3

        stdscr.attron(curses.color_pair(1))
        stdscr.hline(box_start_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.hline(box_end_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.vline(box_start_y + 1, box_start_x, curses.ACS_VLINE, box_end_y - box_start_y - 1)
        stdscr.vline(box_start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE,
                     box_end_y - box_start_y - 1)

        stdscr.addch(box_start_y, box_start_x, curses.ACS_ULCORNER)
        stdscr.addch(box_start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
        stdscr.addch(box_end_y, box_start_x, curses.ACS_LLCORNER)
        stdscr.addch(box_end_y, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

        if (isReadOnly):
            header_text = f"View hosts | {group['name']}"
        else:
            header_text = f"Apply scripts | {group['name']}"
        header_x = box_start_x + 2
        stdscr.addstr(box_start_y, header_x, header_text, curses.A_ITALIC | curses.color_pair(1))
        stdscr.attroff(curses.color_pair(1))

        ###################################################################
        ### Menu items are previously extracted host IP addresses.
        ###################################################################

        for i, host in enumerate(hosts_ips):
            y = box_start_y + i + 2
            x = box_start_x + ((2 * w // 3) - len(host)) // 2

            if i == selected_row:
                if (isReadOnly == False):
                    if i in selected_hosts:
                        stdscr.addstr(y, x, host, curses.color_pair(3) | curses.A_REVERSE)
                    else:
                        stdscr.addstr(y, x, host, curses.color_pair(2) | curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, host, curses.A_REVERSE)
            elif i in selected_hosts:
                stdscr.addstr(y, x, host, curses.color_pair(3))
            else:
                if (isReadOnly == False):
                    stdscr.addstr(y, x, host, curses.color_pair(2))
                else:
                    stdscr.addstr(y, x, host)
            y += 1

        if isReadOnly:
            bottom_message = f"Press 'q' to go back to host groups"
            stdscr.addstr(h - 2, 1, bottom_message, curses.A_ITALIC | curses.A_DIM)
        else:
            bottom_message = f"Press 'q' to go back to host groups"
            stdscr.addstr(h - 4, 1, bottom_message, curses.A_ITALIC | curses.A_DIM)
            bottom_message2 = f"Press 't' to toggle individual selection"
            stdscr.addstr(h - 3, 1, bottom_message2, curses.A_ITALIC | curses.A_DIM)
            bottom_message2 = f"Press 'g' to toggle all host selection. Selected hosts: {selected_hosts}"
            stdscr.addstr(h - 2, 1, bottom_message2, curses.A_ITALIC | curses.A_DIM)
            if (selected_hosts):
                selected_hosts_info = [(hosts_ips[i], hosts_usernames[i], hosts_ports[i]) for i in selected_hosts]
                selected_hostnames, usernames_list, ports_list = zip(*selected_hosts_info)


        ###################################################################
        ### When host is selected (ENTER is pressed), a new window will
        ### be displayed with information about that host.
        ###################################################################

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(hosts_ips) - 1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if isReadOnly:
                host = hosts_ips[selected_row]
                username = hosts_usernames[selected_row]
                port = hosts_ports[selected_row]
                display_info(stdscr, host, port, username)
            else:
                if selected_hosts:  # If selected_hosts is not empty
                    selected_hosts_info = [(hosts_ips[i], hosts_usernames[i], hosts_ports[i]) for i in selected_hosts]
                    selected_hostnames, usernames_list, ports_list = zip(*selected_hosts_info)
                    display_script_menu(stdscr, title, selected_hostnames, usernames_list, ports_list)
                else:
                    host = hosts_ips[selected_row]
                    username = hosts_usernames[selected_row]
                    port = hosts_ports[selected_row]
                    display_script_menu(stdscr, title, [host], [username], [port])
        elif key == ord('g') or key == ord('G'):
            if (isReadOnly == False):
                if len(selected_hosts) == len(hosts_ips):
                    selected_hosts.clear()
                else:
                    selected_hosts = set(range(len(hosts_ips)))
        elif key == ord('t') or key == ord('T'):
            if (isReadOnly == False):
                if selected_row in selected_hosts:
                    selected_hosts.remove(selected_row)
                else:
                    selected_hosts.add(selected_row)
        elif key == ord('q'):
            break

        stdscr.clear()
        stdscr.refresh()
        
def display_info(stdscr, host, port, username):

    stdscr.refresh()
    h, w = stdscr.getmaxyx()
    
    ###################################################################
    ### Get information about logged in users and running services
    ### on that host.
    ###################################################################
    
    users = get_logged_in_users(host, port, username)
    services = get_running_services(host, port, username)
    ports = get_currently_opened_ports(host, port, username)

    ###################################################################
    ### Splits information into an array of strings based on line breaks.
    ###################################################################

    users_lines = users.splitlines()
    services_lines = services.splitlines()
    ports_lines = ports.splitlines()
    
    ###################################################################
    ### Total amount of selectable elements is going to be the sum
    ### of all elements of different information lists plus unintended
    ### lines which include empty lines and headers to show what kind 
    ### of information is presented below.
    ###################################################################
    
    unintented_lines = 8 + 1
    total_height = len(users_lines) + len(services_lines) + len(ports_lines) + unintented_lines

    ###################################################################
    ### Initializes a scrollable pad for displaying information.
    ###################################################################
    
    pad = curses.newpad(total_height, w)
    
    ###################################################################
    ### Tracking current position for user input actions.
    ### pad_pos      - topmost line that is currently seen in the pad.
    ### selected_row - current line that user interacts with.
    ###################################################################
    
    pad_pos = 0
    selected_row = 1
    modal_visible = False

    while True:
        ###################################################################
        ### Clear the pad before each refresh.
        ###################################################################
    
        pad.clear()

        ###################################################################
        ### Display users using get_logged_in_users() function.
        ###################################################################

        users_section_start = 0
        users_section_end = len(users_lines) + 1
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)


        # Draw a box around the users section
        pad.attron(curses.color_pair(1))
        pad.hline(users_section_start, 0, curses.ACS_HLINE, w)
        pad.hline(users_section_end, 0, curses.ACS_HLINE, w)
        pad.vline(users_section_start + 1, 0, curses.ACS_VLINE, users_section_end - users_section_start - 1)
        pad.vline(users_section_start + 1, w - 1, curses.ACS_VLINE, users_section_end - users_section_start - 1)
        pad.addch(users_section_start, 0, curses.ACS_ULCORNER)
        pad.addch(users_section_start, w - 1, curses.ACS_URCORNER)
        pad.addch(users_section_end, 0, curses.ACS_LLCORNER)
        pad.addch(users_section_end, w - 1, curses.ACS_LRCORNER)
        pad.addstr(users_section_start, 2, f"Logged-in users ({len(users_lines)})", curses.A_ITALIC | curses.color_pair(1))
        pad.addstr(users_section_start, w-2-len(host), host, curses.A_ITALIC | curses.color_pair(1))
        pad.attroff(curses.color_pair(1))

        # Add the users information inside the border
        for i, user in enumerate(users_lines, start=1):
            if i == selected_row:
                pad.addstr(i, 1, "[X]", curses.A_REVERSE)
                pad.addstr(i, 5, user, curses.A_REVERSE)
            else:
                pad.addstr(i, 1, "[X]")
                pad.addstr(i, 5, user)
        
        ###################################################################
        ### Display running services using get_running_services() function.
        ###
        ### (i-2) is for not counting header and empty line in between lists
        ### Truncate long service names if they exceed terminal width.
        ###################################################################

        services_section_start = users_section_end + 1
        services_section_end = services_section_start + len(services_lines) + 1

        # Draw a box around the services section
        pad.attron(curses.color_pair(1))
        pad.hline(services_section_start, 0, curses.ACS_HLINE, w)
        pad.hline(services_section_end, 0, curses.ACS_HLINE, w)
        pad.vline(services_section_start + 1, 0, curses.ACS_VLINE, services_section_end - services_section_start - 1)
        pad.vline(services_section_start + 1, w - 1, curses.ACS_VLINE,
                  services_section_end - services_section_start - 1)
        pad.addch(services_section_start, 0, curses.ACS_ULCORNER)
        pad.addch(services_section_start, w - 1, curses.ACS_URCORNER)
        pad.addch(services_section_end, 0, curses.ACS_LLCORNER)
        pad.addch(services_section_end, w - 1, curses.ACS_LRCORNER)
        pad.addstr(services_section_start, 2, f"Running services ({len(services_lines)})", curses.A_ITALIC | curses.color_pair(1))
        pad.attroff(curses.color_pair(1))

        for i, service in enumerate(services_lines, start=services_section_start + 1):
            if (i - 2) == selected_row:
                pad.addstr(i, 1, f"[X]", curses.A_REVERSE)
                if len(service) > w - 5:
                    truncated_service = service[:w - 5]
                    pad.addstr(i, 4, truncated_service, curses.A_REVERSE)
                else:
                    pad.addstr(i, 4, service, curses.A_REVERSE)
            else:
                pad.addstr(i, 1, f"[X]")
                if len(service) > w - 5:
                    truncated_service = service[:w - 5]
                    pad.addstr(i, 4, truncated_service)
                else:
                    pad.addstr(i, 4, service)

        ports_section_start = len(users_lines) + len(services_lines) + 4
        ports_section_end = ports_section_start + len(ports_lines) + 1

        # Draw a box around the ports section
        pad.attron(curses.color_pair(1))
        pad.hline(ports_section_start, 0, curses.ACS_HLINE, w)
        pad.hline(ports_section_end, 0, curses.ACS_HLINE, w)
        pad.vline(ports_section_start + 1, 0, curses.ACS_VLINE, ports_section_end - ports_section_start - 1)
        pad.vline(ports_section_start + 1, w - 1, curses.ACS_VLINE, ports_section_end - ports_section_start - 1)
        pad.addch(ports_section_start, 0, curses.ACS_ULCORNER)
        pad.addch(ports_section_start, w - 1, curses.ACS_URCORNER)
        pad.addch(ports_section_end, 0, curses.ACS_LLCORNER)
        pad.addch(ports_section_end, w - 1, curses.ACS_LRCORNER)
        pad.addstr(ports_section_start, 2, f"Currently opened ports ({len(ports_lines)})", curses.A_ITALIC | curses.color_pair(1))
        pad.attroff(curses.color_pair(1))
        
        for i, port_info in enumerate(ports_lines, start=len(services_lines) + len(users_lines) + 5):
            if (i-4) == selected_row:
                # Skip [X] prefix for the first element
                if i != len(services_lines) + len(users_lines) + 5:
                    pad.addstr(i, 1, f"[X]", curses.A_REVERSE)
                if len(port_info) > w - 5:
                    truncated_port = port_info[:w - 5]
                    pad.addstr(i, 4, truncated_port, curses.A_REVERSE)
                else:
                    pad.addstr(i, 4, port_info, curses.A_REVERSE)
            else:
                # Skip [X] prefix for the first element
                if i != len(services_lines) + len(users_lines) + 5:
                    pad.addstr(i, 1, f"[X]")
                if len(port_info) > w - 5:
                    truncated_port = port_info[:w - 5]
                    pad.addstr(i, 4, truncated_port)
                else:
                    pad.addstr(i, 4, port_info)
        ###################################################################
        ### Display footer:
        ### Selected row and onIt are left for debugging.
        ###
        ### onIt represents the line where user currently is. Because of TUI
        ### lines peculiar indexing, selected_row doesn't actually represent
        ### the line of information where user currently stands. This is 
        ### because we leave some lines not to be selectable, like headers
        ### such as "Logged in users" and "Running services", as well as 
        ### empty lines after each list.
        ###
        ### find_selected_element() maps currently highlighted row with actual
        ### data where user thinks he is.
        ###################################################################
        
        onIt, family = find_selected_element_in_host_info(selected_row, users_lines, services_lines, ports_lines)


        #bottom_message = (f"Press 'q' to go back to the main menu, selected row is {selected_row}, "
        #                  f"onIt = {onIt.split()[0] + '                '} ")
        #bottom_message = (f"Press 'q' to go back to the main menu, selected row is {selected_row}, "
        #                  f"pad_pos = {pad_pos}, modalVisible = {modal_visible}            ")
        bottom_message = (f"Press 'h' to open context menu                               ")
        stdscr.addstr(h - 3, 0, " " * w)
        stdscr.addstr(h - 2, 0, bottom_message, curses.A_DIM | curses.A_ITALIC)

        def draw_modal(pad, pad_pos):
            modal_width = 45
            modal_height = 11
            modal_text = ("Context information:"
                          "\n\nSPACE - scroll whole page down"
                          "\ny / Y - scroll whole page up\ng / G - scroll to next info tab"
                          "\nb / B - scroll to previous info tab\n\nq / Q - go back to host list"
                          "\nh / H - close context menu")
            # Calculate the position to draw the modal (top-right corner)
            modal_y = pad_pos+1
            modal_x = pad.getmaxyx()[1] - modal_width - 1

            for y in range(modal_y, modal_y + modal_height):
                pad.addstr(y, modal_x, ' ' * modal_width)

            # Create a window for the modal
            modal_win = pad.subpad(modal_height, modal_width, modal_y, modal_x)

            # Clear the area behind the modal

            # Draw the box for the modal
            curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            modal_win.attron(curses.color_pair(2))
            modal_win.box()

            # Add the modal text inside the box
            modal_text_lines = modal_text.split('\n')
            for i, line in enumerate(modal_text_lines):
                if i == 0:  # Skip applying bold to the first line
                    modal_win.addstr(i + 1, 1, line[:modal_width - 2].ljust(modal_width - 2))
                else:
                    prefix = line[:5]
                    suffix = line[5:]
                    # Apply bold attribute to the prefix
                    modal_win.addstr(i + 1, 1, prefix, curses.A_BOLD | curses.color_pair(2))
                    # Add the remaining part of the line without bold attribute
                    modal_win.addstr(suffix)
            modal_win.attroff(curses.color_pair(2))

        ###################################################################
        ### Display the pad content on the screen.
        ### Adjust height to fit in the terminal, leave space for footer.
        ###################################################################
        if modal_visible:
            draw_modal(pad, pad_pos)
        pad.refresh(pad_pos, 0, 0, 0, h-3, w-1)

        ###################################################################
        ### Get user input:
        ### q     - go back to the main menu.
        ### UP    - change the selected row to one higher if possible.
        ### DOWN  - change the selected row to one lower if possible.
        ### ENTER - open action confirmation modal.
        ###################################################################

        # pad_unintented_lines = h - shown_info

        key = stdscr.getch()
        if key == ord('q'):
            break
        if key == curses.KEY_UP:
            selected_row = max(1, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = selected_row - 1
        elif key == curses.KEY_DOWN:
            selected_row = min((len(users_lines)+len(services_lines)+len(ports_lines)), selected_row + 1)
            if selected_row >= pad_pos + h - unintented_lines:
                pad_pos = min(selected_row - h + unintented_lines, total_height - h)
        if key == ord(' '):
            selected_row = min((len(users_lines)+len(services_lines)+len(ports_lines)), pad_pos + h - 3)
            pad_pos = min(total_height-h, h)
        if key == ord('y') or key == ord('Y'):
            selected_row = max(1, selected_row-h)
            if selected_row <= pad_pos:
                pad_pos = max(0, selected_row-1)
        if key == ord('g') or key == ord('G'):
            # Jump to the next family list
            if family == "USERS":
               selected_row = min((len(users_lines)+len(services_lines)+len(ports_lines)), len(users_lines)+1)
            if family == "SERVICES":
               selected_row = min((len(users_lines)+len(services_lines)+len(ports_lines)), len(users_lines)+len(services_lines)+1)
            if selected_row >= pad_pos + h-6:
                pad_pos = min(selected_row - h + 8, selected_row+3)
        if key == ord('b') or key == ord('B'):
            # Jump to the previous family list
            if family == "SERVICES":
               selected_row = 1
            if family == "PORTS":
               selected_row = len(users_lines)+1
            if selected_row <= pad_pos:
                pad_pos = max(0, selected_row-1)
        if key == ord('h'):
            modal_visible = not modal_visible
        if key == curses.KEY_ENTER or key == 10:
            confirmation_modal(stdscr, onIt, family, h, w, host, port, username)
            
def find_selected_element_in_host_info(selected_row, users_lines, services_lines, ports_lines):

    ###################################################################
    ### Mapping selected_row with real elements in lists, because when
    ### jumping we skip headers and empty lines
    ###
    ### selected_row-1 everywhere is because arrays starting index is 0,
    ### but selected_row starts from 1.
    ###################################################################
    
    selected_element = 'UNDEFINED'
    family = ''
    
    if selected_row <= len(users_lines)+len(services_lines)+len(ports_lines)+6:
       if selected_row <= len(users_lines):
        selected_element = users_lines[selected_row-1]
        family = "USERS"
       elif selected_row <= len(users_lines)+len(services_lines):
        selected_element = services_lines[selected_row-len(users_lines)-1]
        family = "SERVICES"
       elif selected_row >= len(users_lines)+len(services_lines):
        selected_element = ports_lines[selected_row-len(users_lines)-len(services_lines)-1]
        family = "PORTS"

    return selected_element, family

def confirmation_modal(stdscr, onIt, family, height, width, host, port, username):
 
    ###################################################################
    ### display_modal - modal which is called from individual host
    ### window when viewing information about it and want to terminate
    ### a specific process from the list.
    ###################################################################
    
    ###################################################################
    ### Center the modal, place it on top of the screen.
    ### modal_y and modal_x represent the top-left corner coordinates.
    ###################################################################
    
    center_y = height // 2
    center_x = width // 2
    
    modal_height = 16
    modal_width = width - 10
    
    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2
    
    ###################################################################
    ### Initialize the modal, add border to it.
    ### Initialize coloured pair to use different colouring for some
    ### text in the modal to drag attention.
    ###################################################################
    
    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()
    
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    
    ###################################################################
    ### 'who' represents the specific element which will be terminated.
    ### Used in modal confirmation text.
    ###################################################################
    
    who = onIt.split()[0]
    
    ###################################################################
    ### Depending on for which process this modal is (user, service, 
    ### etc.), it will show different confirmation modal text.
    ###
    ### 'family' is the parameter to name which process to kill. It
    ### is in the find_selected_element_in_host_info() for the row
    ### on which user currently stands when watching individual host
    ### information.
    ###################################################################   
    
    if family == "USERS":
        withWhat = onIt.split()[1]
        modal.addstr(1, 2, f'KILLING USER {who} .', curses.color_pair(3))
        modal.addstr(3, 2, 'Are you sure?', curses.A_BOLD | curses.A_UNDERLINE)
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.addstr(10, 2, '')
        modal.refresh()
    if family == "SERVICES":
        withWhat = onIt.split()[0]
        modal.addstr(1, 2, f'KILLING SERVICE {who} .', curses.color_pair(3))
        modal.addstr(3, 2, 'Are you sure?', curses.A_BOLD | curses.A_UNDERLINE)
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.addstr(10, 2, '')
        modal.refresh()
    
    ###################################################################
    ### Get user input:
    ### ENTER - confirm action presented in the modal and initiate
    ### corresponding script to fulfill it.
    ### q     - close the modal
    ###################################################################
    
    while True:
        key = stdscr.getch()
        if key == curses.KEY_ENTER or key == 10:
            if family == "USERS": 
                run_shell_script("kill_login_session", host, port, username, withWhat)
                modal.addstr(5, 2, f"SUCCESS", curses.A_BOLD)
            if family == "SERVICES":
                run_shell_script("kill_service_by_name", host, port, username, withWhat)
                modal.addstr(5, 2, f"SUCCESS", curses.A_BOLD)
            modal.refresh()
        elif key == ord('q'):
            break 
        
def display_script_menu(stdscr, title, hosts, usernames, ports):

    ###################################################################
    ### display_script_menu() - final menu where user can view and
    ### select scripts or scans which are to be run on the selected
    ### host.
    ###################################################################
    
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    ###################################################################
    ### selected_row is initiated from 3 becase we want to leave some
    ### space at the top to display how many hosts are we applying the
    ### scripts to.
    ###
    ### We will not be able to jump to lesser rows.
    ###################################################################
    title_x = w // 2 - len(title[0]) // 2
    title_y = 2
    selected_row = title_y + len(title) + 4
    
    ###################################################################
    ### script_lines - an array with the names of the scripts that
    ### can be chosen. Will grow when new modules are added.
    ###
    ### script_x - an array containing x axis information of where to
    ### place corresponding menu option. The rows are incrementory
    ### by 2 so that they are not close together (for greater appeal).
    ###################################################################
    
    script_lines = ["CHECK PORTS", "MAKE BACKUPS", "RUN LYNIS SCAN", "MANIFEST", "CHECK ROOTKIT", "AUDIT SETUP", "AUDIT RETRIEVAL", "CUSTOM COMMAND"]
    script_x = [title_y + len(title) + 4, title_y + len(title) + 5, title_y + len(title) + 6, title_y + len(title) + 7, title_y + len(title) + 8, title_y + len(title) + 9, title_y + len(title) + 10, title_y + len(title) + 11]

    ###################################################################
    ### Below we initialize and assign values from our documentation
    ### for each host which hosts should be open and which directories
    ### should be backed up.
    ###
    ### It reads from doc_file where all of relevant information for
    ### each host will be present.
    ###################################################################

    doc_ports = [[] for _ in range(len(hosts))]
    doc_locations = [[] for _ in range(len(hosts))]
    doc_manifests = [[] for _ in range(len(hosts))]
    doc_chkrootkit = [[] for _ in range(len(hosts))]
    doc_audit = [[] for _ in range(len(hosts))]
    for i, host in enumerate(hosts):
        doc_ports[i] = functions.get_elements_for_ip(host, "ports")
        doc_locations[i] = functions.get_elements_for_ip(host, "copy_locations")
        doc_manifests[i] = functions.get_elements_for_ip(host, "manifest_dirs")
        doc_chkrootkit[i] = functions.get_elements_for_ip(host, "chkrootkit")
        doc_audit[i] = functions.get_elements_for_ip(host, "audit_dirs")
      
    ###################################################################
    ### Displaying menu options, highlighting when current row matches.
    ###
    ### When ENTER is pressed for the current row, a modal will appear
    ### to guide user for further actions. Depending on which script
    ### is to run, a modal with different parameters will open.
    ###################################################################
    while True:

        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        for i, line in enumerate(title):
            stdscr.addstr(title_y + i, title_x, line, curses.color_pair(1))

        box_start_y = title_y + len(title) + 2
        box_end_y = box_start_y + len(script_lines) + 3
        box_start_x = (w - (2 * w // 3)) // 2  # (Centered horizontally)
        box_end_x = 2 * w // 3

        stdscr.attron(curses.color_pair(1))
        stdscr.hline(box_start_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.hline(box_end_y, box_start_x, curses.ACS_HLINE, box_end_x)
        stdscr.vline(box_start_y + 1, box_start_x, curses.ACS_VLINE, box_end_y - box_start_y - 1)
        stdscr.vline(box_start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE,
                     box_end_y - box_start_y - 1)

        stdscr.addch(box_start_y, box_start_x, curses.ACS_ULCORNER)
        stdscr.addch(box_start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
        stdscr.addch(box_end_y, box_start_x, curses.ACS_LLCORNER)
        stdscr.addch(box_end_y, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

        header_text = "Script menu"
        header_x = box_start_x + 2
        stdscr.addstr(box_start_y, header_x, header_text, curses.A_ITALIC | curses.color_pair(1))
        stdscr.attroff(curses.color_pair(1))

        stdscr.addstr(script_x[0], w // 2 - len(script_lines[0]) // 2, script_lines[0], curses.A_NORMAL)
        stdscr.addstr(script_x[1], w // 2 - len(script_lines[1]) // 2, script_lines[1], curses.A_NORMAL)
        stdscr.addstr(script_x[2], w // 2 - len(script_lines[2]) // 2, script_lines[2], curses.A_NORMAL)
        stdscr.addstr(script_x[3], w // 2 - len(script_lines[3]) // 2, script_lines[3], curses.A_NORMAL)
        stdscr.addstr(script_x[4], w // 2 - len(script_lines[4]) // 2, script_lines[4], curses.A_NORMAL)
        stdscr.addstr(script_x[5], w // 2 - len(script_lines[5]) // 2, script_lines[5], curses.A_NORMAL)
        stdscr.addstr(script_x[6], w // 2 - len(script_lines[6]) // 2, script_lines[6], curses.A_NORMAL)
        stdscr.addstr(script_x[7], w // 2 - len(script_lines[7]) // 2, script_lines[7], curses.A_NORMAL)
        
        if selected_row == script_x[0]:
            stdscr.addstr(script_x[0], w // 2 - len(script_lines[0]) // 2, script_lines[0], curses.A_REVERSE)
        if selected_row == script_x[1]:
            stdscr.addstr(script_x[1], w // 2 - len(script_lines[1]) // 2, script_lines[1], curses.A_REVERSE)
        if selected_row == script_x[2]:
            stdscr.addstr(script_x[2], w // 2 - len(script_lines[2]) // 2, script_lines[2], curses.A_REVERSE)
        if selected_row == script_x[3]:
            stdscr.addstr(script_x[3], w // 2 - len(script_lines[3]) // 2, script_lines[3], curses.A_REVERSE)
        if selected_row == script_x[4]:
            stdscr.addstr(script_x[4], w // 2 - len(script_lines[4]) // 2, script_lines[4], curses.A_REVERSE)
        if selected_row == script_x[5]:
            stdscr.addstr(script_x[5], w // 2 - len(script_lines[5]) // 2, script_lines[5], curses.A_REVERSE)
        if selected_row == script_x[6]:
            stdscr.addstr(script_x[6], w // 2 - len(script_lines[6]) // 2, script_lines[6], curses.A_REVERSE)
        if selected_row == script_x[7]:
            stdscr.addstr(script_x[7], w // 2 - len(script_lines[7]) // 2, script_lines[7], curses.A_REVERSE)

        bottom_message = f"Press 'q' to go back to all hosts"
        stdscr.addstr(h-2, 1, f"Selected hosts: {hosts}", curses.A_ITALIC | curses.A_DIM)
        stdscr.addstr(h-3, 1, bottom_message, curses.A_ITALIC | curses.A_DIM)
        
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(title_y + len(title) + 4, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(title_y + len(title) + 11, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_row == script_x[0]:
                script_menu_modal(stdscr, 'PORTS', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
            if selected_row == script_x[1]:
                script_menu_modal(stdscr, 'BACKUP', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
            if selected_row == script_x[2]:
                script_menu_modal(stdscr, 'LYNIS', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
            if selected_row == script_x[3]:
                script_menu_modal(stdscr, 'MANIFEST', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
            if selected_row == script_x[4]:
                script_menu_modal(stdscr, 'CHKROOTKIT', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
            if selected_row == script_x[5]:
                script_menu_modal(stdscr, 'AUDIT_SETUP', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
            if selected_row == script_x[6]:
                script_menu_modal(stdscr, 'AUDIT_RETRIEVE', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
            if selected_row == script_x[7]:
                script_menu_modal(stdscr, 'CUSTOM_COMMAND', h, w, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit)
        elif key == ord('q'):
            break

        stdscr.clear()
        stdscr.refresh()

def script_menu_modal(stdscr, family, height, width, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests, doc_chkrootkit, doc_audit):
    
    ###################################################################
    ### script_menu_modal() - modal which will be called when some
    ### kind of confirmation or guidance is needed to proceed with
    ### the selected script to apply to host(s).
    ##################################################################

    center_y = height // 2
    center_x = width // 2
    
    modal_height = 12
    modal_width = width - 10
    
    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2
   
    
    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()
    
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    
    ###################################################################
    ### Depending on for which script this modal is, it will add
    ### different content to it.
    ###
    ### 'family' is the parameter to name which script to run, it
    ### is determined based on which row the user was when ENTER was
    ### pressed in the script menu.
    ###################################################################

    if family == "PORTS":
        modal.addstr(1, 2, f"Enter ports separated by spaces to check if they are open on remote host.")
        modal.addstr(2, 2, f"Press ENTER to use information from doc_file.")
        modal.addstr(9, 2, 'Press ENTER to confirm')
        modal.addstr(10, 2, 'Press q to cancel')
        modal.refresh()

        ###################################################################
        ### Here input can only be numeric because we need to pass port
        ### numbers. Any other symbol will be dropped except for 'q' which
        ### will quit the modal.
        ###################################################################
        
        def is_numeric_char(char):
            if isinstance(char, str):
                return char.isdigit() or char == ' '
            elif isinstance(char, int):
                return chr(char).isdigit() or char == ord(' ')
            else:
                return False

        port_input = ''
        ###################################################################
        ### curses.echo() - enables character echoing, what is typed is 
        ### showed.
        ### stdscr.move() - positions the cursor to a specific location on
        ### the modal.
        ### stdscr.clrtoeol() - clears the line before writing
        ###################################################################
        
        while True:
            curses.echo()
            stdscr.move(modal_y + 4, modal_x + 2)
            stdscr.clrtoeol() 
            stdscr.addstr(modal_y + 4, modal_x + 2, port_input)
            curses.noecho()
            
            key = stdscr.getch()
            
            if key == curses.KEY_ENTER or key in [10, 13]:
                if port_input == '':
                    get_port_info(hosts, ports, usernames, *doc_ports)
                else:
                    portsss = port_input.split()
                    get_port_info(hosts, ports, usernames, *portsss)
                modal.addstr(7, 2, f"Ports file created in tengui/ ", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                port_input = port_input[:-1]
            elif is_numeric_char(key):
                port_input += chr(key)
        
    ###################################################################
    ### for BACKUP and LYNIS connection with back end script logic 
    ### is NOT IMPLEMENTED YET.
    ###################################################################
    
    if family == "BACKUP":
        directory_input = ''
        
        modal.addstr(1, 2, "Enter absolute paths of folders separated by spaces (ex. /home/user/testdir).")
        modal.addstr(2, 2, f"Press ENTER to use information from doc_file.")
        modal.addstr(9, 2, 'Press ENTER to confirm')
        modal.addstr(10, 2, 'Press q to go back')
        
        modal.refresh()
         
        while True:
            curses.echo()
            stdscr.move(modal_y + 4, modal_x + 2)
            stdscr.clrtoeol() 
            stdscr.addstr(modal_y + 4, modal_x + 2, directory_input)
            curses.noecho()
            modal.addstr(10, 2, 'Press q to go back')
            
            key = stdscr.getch()
            
            if key == curses.KEY_ENTER or key in [10, 13]:
                if directory_input == '':
                    run_backup_script(hosts, ports, usernames, *doc_locations)
                else:
                    folders = directory_input.split()
                    run_backup_script(hosts, ports, usernames, *folders)
                modal.addstr(7, 2, "Folders backed up!", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                directory_input = directory_input[:-1]
            else:
                directory_input += chr(key) 
                modal.refresh()
                
    if family == "LYNIS":
        modal.addstr(1, 2, "Lynis Scan proccess will be run in the background.")
        modal.addstr(2, 2, f"Press ENTER to confirm.")
        modal.addstr(10, 2, 'Press q to cancel')
        modal.refresh()

        while True:        
            key = stdscr.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                modal.addstr(4, 2, 'Scan started, you can exit this window.')
                modal.addstr(5, 2, 'Results will be in /tengui/modules/lynisCan')
                modal.refresh()
                run_lynis(usernames, hosts, ports)
                modal.refresh()
            elif key == ord('q'):
                break

    if family == "MANIFEST":
        directory_input = ''

        flattened_list = [item for sublist in doc_manifests for item in sublist]

        modal.addstr(1, 2, "Enter absolute paths of folders separated by spaces (ex. /home/user/testdir).")
        modal.addstr(2, 2, f"Press ENTER to use information from doc_file.")
        modal.addstr(3, 2, 'Results will be in /tengui/modules/hasher')
        modal.addstr(9, 2, 'Press ENTER to confirm')
        modal.addstr(10, 2, 'Press q to go back')

        modal.refresh()

        while True:
            curses.echo()
            stdscr.move(modal_y + 4, modal_x + 2)
            stdscr.clrtoeol()
            stdscr.addstr(modal_y + 4, modal_x + 2, directory_input)
            curses.noecho()
            modal.addstr(10, 2, 'Press q to go back')

            key = stdscr.getch()

            if key == curses.KEY_ENTER or key in [10, 13]:
                if directory_input == '':
                    run_manifest_script(hosts, ports, usernames, *flattened_list)
                else:
                    folders = directory_input.split()
                    run_manifest_script(hosts, ports, usernames, *folders)
                modal.addstr(7, 2, "Folders hashed and sent!", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                directory_input = directory_input[:-1]
            else:
                directory_input += chr(key)
                modal.refresh()

    if family == "CHKROOTKIT":
        directory_input = ''

        modal.addstr(1, 2, "Enter absolute paths of folders separated by spaces (ex. /home/user/testdir).")
        modal.addstr(2, 2, f"Press ENTER to use information from doc_file.")
        modal.addstr(3, 2, 'Results will be in /tengui/modules/chkrootkit')
        modal.addstr(9, 2, 'Press ENTER to confirm')
        modal.addstr(10, 2, 'Press q to go back')

        modal.refresh()

        while True:
            curses.echo()
            stdscr.move(modal_y + 4, modal_x + 2)
            stdscr.clrtoeol()
            stdscr.addstr(modal_y + 4, modal_x + 2, directory_input)
            curses.noecho()
            modal.addstr(10, 2, 'Press q to go back')

            key = stdscr.getch()

            if key == curses.KEY_ENTER or key in [10, 13]:
                if directory_input == '':
                    run_chkrootkit_script(hosts, ports, usernames, *doc_chkrootkit)
                else:
                    folders = directory_input.split()
                    run_chkrootkit_script(hosts, ports, usernames, *folders)
                modal.addstr(7, 2, "Chkrootkit successful", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                directory_input = directory_input[:-1]
            else:
                directory_input += chr(key)
                modal.refresh()

    if family == "AUDIT_SETUP":
        directory_input = ''

        modal.addstr(1, 2, "Enter absolute paths of folders separated by spaces (ex. /home/user/testdir).")
        modal.addstr(9, 2, 'Press ENTER to confirm')
        modal.addstr(10, 2, 'Press q to go back')

        modal.refresh()

        while True:
            curses.echo()
            stdscr.move(modal_y + 4, modal_x + 2)
            stdscr.clrtoeol()
            stdscr.addstr(modal_y + 4, modal_x + 2, directory_input)
            curses.noecho()
            modal.addstr(10, 2, 'Press q to go back')

            key = stdscr.getch()

            if key == curses.KEY_ENTER or key in [10, 13]:
                if directory_input == '':
                    run_audit_setup_script(hosts, ports, usernames, *doc_audit)
                else:
                    folders = directory_input.split()
                    run_audit_setup_script(hosts, ports, usernames, *folders)
                modal.addstr(7, 2, "Audit successful", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                directory_input = directory_input[:-1]
            else:
                directory_input += chr(key)
                modal.refresh()

    if family == "AUDIT_RETRIEVE":
        directory_input = ''

        modal.addstr(1, 2, "Enter absolute paths of folders separated by spaces (ex. /home/user/testdir).")
        modal.addstr(2, 2, f"Press ENTER to use information from doc_file.")
        modal.addstr(3, 2, 'Results will be in /tengui/modules/audit')
        modal.addstr(9, 2, 'Press ENTER to confirm')
        modal.addstr(10, 2, 'Press q to go back')

        modal.refresh()

        while True:
            curses.echo()
            stdscr.move(modal_y + 4, modal_x + 2)
            stdscr.clrtoeol()
            stdscr.addstr(modal_y + 4, modal_x + 2, directory_input)
            curses.noecho()
            modal.addstr(10, 2, 'Press q to go back')

            key = stdscr.getch()

            if key == curses.KEY_ENTER or key in [10, 13]:
                if directory_input == '':
                    run_audit_retrieve_script(hosts, ports, usernames, *doc_audit)
                else:
                    folders = directory_input.split()
                    run_audit_retrieve_script(hosts, ports, usernames, *folders)
                modal.addstr(7, 2, "Audit logs formed", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                directory_input = directory_input[:-1]
            else:
                directory_input += chr(key)
                modal.refresh()

    if family == "CUSTOM_COMMAND":
        directory_input = ''

        modal.addstr(1, 2, "Write a one-liner command which will execute on the remote host(s).")
        modal.addstr(2, 2, f"Press ENTER to use information from doc_file.")
        modal.addstr(3, 2, 'Results will be in /tengui/modules/runCmd')
        modal.addstr(9, 2, 'Press ENTER to confirm')
        modal.addstr(10, 2, 'Press q to go back')

        modal.refresh()

        while True:
            curses.echo()
            stdscr.move(modal_y + 4, modal_x + 2)
            stdscr.clrtoeol()
            stdscr.addstr(modal_y + 4, modal_x + 2, directory_input)
            curses.noecho()
            modal.addstr(10, 2, 'Press q to go back')

            key = stdscr.getch()

            if key == curses.KEY_ENTER or key in [10, 13]:
                if directory_input == '':
                    run_custom_command_script(hosts, ports, usernames, *doc_audit)
                else:
                    run_custom_command_script(hosts, ports, usernames, directory_input)
                modal.addstr(7, 2, "Commands ran successfully", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                directory_input = directory_input[:-1]
            else:
                directory_input += chr(key)
                modal.refresh()


script_paths = {
    "check_ports": "./modules/ports/check.sh",
    "kill_service_by_name": "./modules/actions/kill_service_by_name.sh",
    "kill_login_session": "./modules/actions/kill_login_session.sh",
    "get_currently_opened_ports": "./modules/ports/check_currently_opened_ports.sh",
    "hasher": "./modules/hasher/hasher.sh",
}

def run_shell_script(script_name, host, port, username, *args):
    try:
        ###################################################################
        ### Initializing SSH session using paramiko, loads system host keys
        ### and adds unknown to the known_hosts file.
        ###################################################################
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, port=port, username=username)

        ###################################################################
        ### Verifying that SSH connection is active. If it is active,
        ### proceed with initiating the script from the script path
        ### dictionary.
        ###################################################################

        if not ssh_client.get_transport().is_active():
            print("SSH connection is not alive.")
            return None

        script_path = script_paths.get(script_name)
        if script_path is None:
            print(f"Error: Script '{script_name}' not found.")
            return None

        ###################################################################
        ### For executing remote script from REMOTE machine: 
        ###################################################################

#        with open(script_path, 'r') as file:
#            script_content = file.read()
#
#        remote_script_path = f"/home/{username}/{script_name}"
#        with ssh_client.open_sftp() as sftp:
#            with sftp.file(remote_script_path, 'w') as remote_file:
#                remote_file.write(script_content)
#
#        ssh_client.exec_command(f"chmod +x {remote_script_path}")
#
#        command = f"{remote_script_path} {' '.join(args)}"
#        stdin, stdout, stderr = ssh_client.exec_command(command)

        ###################################################################
        ### For executing remote script from LOCAL machine: 
        ###################################################################
        
        with open(script_path, 'r') as file:
            script_content = file.read()

        command = f"sudo bash -s {' '.join(args)}"
        stdin, stdout, stderr = ssh_client.exec_command(command)

        stdin.write(script_content)
        stdin.channel.shutdown_write()

        ###################################################################
        ### Saving output to the text file (logs)
        ###################################################################

        output = stdout.read().decode()
        output_file_path = f"./{host}-{script_name}.info"
        with open(output_file_path, 'w') as output_file:
            output_file.write(output)
        return output
    except Exception as e:
        print("Error", e)
        return None
    finally:
        if ssh_client:
            ssh_client.close()

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

# def execute_command(command):
#     subprocess.run(command, shell=True)


def get_logged_in_users(host, port, username):
    command = f'ssh -o StrictHostKeyChecking=yes -p {port} {username}@{host} who'
    return execute_command(command)

def get_running_services(host, port, username):
    command = f'ssh -o StrictHostKeyChecking=yes -p {port} {username}@{host} systemctl list-units --type=service --state=running | grep -v "LOAD   =" | grep -v "ACTIVE =" | grep -v "SUB    =" | grep -v "loaded units listed" | grep -v "^$" | grep -v "UNIT"' 
    return execute_command(command)

def get_currently_opened_ports(host, port, username):
    command = f'ssh -o StrictHostKeyChecking=no -p {port} {username}@{host} sudo lsof -i -P -n'
    return execute_command(command)
    #return run_shell_script("get_currently_opened_ports", host, port, username)
    
def run_backup_script(hosts, ports, usernames, *folders):
    commands = []
    for i, _ in enumerate(hosts):
        folders_str = ' '.join(folders[i-1])
        command = f"./modules/backup/backupFiles.sh {usernames[i-1]} {hosts[i-1]} {ports[i-1]} {folders_str} > /dev/null 2>&1"
        commands.append(command)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0
    
def run_lynis(usernames, hosts, ports):
    commands = []
    for i, _ in enumerate(hosts):
        command = f"./modules/lynisCan/lynis.sh {usernames[i-1]} {hosts[i-1]} {ports[i-1]} > /dev/null 2>&1 &"
        commands.append(command)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0


#SINGLY COMMENTED IN THIS BLOCK IS AN APPROACH OF RUNNING MULTIPLE HOSTS ONE AFTER ANOTHER
#DOUBLY COMMENTED IS THE PREVIOUS APPROACH OF RUNNING ONE HOST, AS PER PREVIOUS SINGULAR MENU OPTION
# def run_manifest_script(hosts, ports, usernames, *folders):
#     print(folders)
#     for i, _ in enumerate(hosts):
#         #run_shell_script("hasher", hosts[i - 1], ports[i - 1], usernames[i - 1], *folders[i - 1])
#         folders_str = ' '.join(folders[i])
#         #command = f"./modules/hasher/hasher.sh {usernames[i]} {hosts[i]} {ports[i]} {folders_str}"
#         command = f"./modules/hasher/hasher.sh {usernames[i]} {hosts[i]} {ports[i]} {folders[i]}"
#         #print("i: " + hosts[i - 1] + " " + ports[i - 1] + " " + usernames[i - 1])
#         print("Hshng: " + hosts[i - 1])
#         execute_command(command)
#     return 0

#RUNNING ALL HOSTS CONCURRENTLY
def run_manifest_script(hosts, ports, usernames, *folders):
    commands = []
    for i, _ in enumerate(hosts):
        folders_str = ' '.join(folders[i])
        command = f"./modules/hasher/hasher.sh {usernames[i]} {hosts[i]} {ports[i]} {folders[i]} > /dev/null 2>&1"
        commands.append(command)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0

def run_chkrootkit_script(hosts, ports, usernames, *folders):
    commands = []
    for i, _ in enumerate(hosts):
        # folders_str = ' '.join(folders[i])
        command = f"./modules/chkrootkit/rootkit.sh {usernames[i]} {hosts[i]} {ports[i]} > /dev/null 2>&1"
        commands.append(command)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0

def run_audit_setup_script(hosts, ports, usernames, *folders):
    commands = []
    for i, _ in enumerate(hosts):
        folders_str = ' '.join(folders[i])
        command = f"./modules/audit/setup.sh {usernames[i]} {hosts[i]} {ports[i]} {folders_str} > /dev/null 2>&1"
        commands.append(command)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0

def run_audit_retrieve_script(hosts, ports, usernames, *folders):
    commands = []
    for i, _ in enumerate(hosts):
        folders_str = ' '.join(folders[i])
        command = f"./modules/audit/retrieve.sh {usernames[i]} {hosts[i]} {ports[i]} {folders_str} > /dev/null 2>&1"
        commands.append(command)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0
def get_port_info(hosts, ports, usernames, *args):
    print(args)
    for i, _ in enumerate(hosts):
        run_shell_script("check_ports", hosts[i-1], ports[i-1], usernames[i-1], *args[i-1])
    return 0

def run_custom_command_script(hosts, ports, usernames, custom_commands):
    commands = []
    print(f" sent {custom_commands} ")
    for i, _ in enumerate(hosts):
        command = f"./modules/runCmd/runCmd.sh {usernames[i]} {hosts[i]} {ports[i]} {custom_commands}"
        commands.append(command)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0

if __name__ == "__main__":
    curses.wrapper(main)
