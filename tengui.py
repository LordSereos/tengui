###################################################################
### Tengui TUI author:
### Martin Martijan
###################################################################

import curses
import subprocess

def main(stdscr):

    ###################################################################
    ### Setting up TUI:
    ### curs_set(0) disables the cursor
    ### init_pair() initializes a color pair for use in the interface
    ###################################################################
    
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    ###################################################################
    ### Read from hosts file to retrieve desired hosts
    ### hosts file should be in the same directory as this script
    ###################################################################
    
    hosts = []
    usernames = []

    with open('hosts', 'r') as file:
        for line in file:
            # Split each line by whitespace
            parts = line.split()
            if len(parts) >= 2:
                # Extract IP and username
                ip_address = parts[0]
                username = parts[1]
                hosts.append(ip_address)
                usernames.append(username)
               
    ###################################################################
    ### selected_row is used for tracking the line which user interacts with
    ### Calling display_menu() function with screen parameters and hosts
    ###################################################################
    
    selected_row = 0
    display_menu(stdscr, hosts, selected_row)


    ###################################################################
    ### Captures user input
    ### Keyboard keys UP and DOWN manage current_row
    ### Enter enforces action on the current line (current_row)
    ### q is used to go back or quit the TUI
    ###################################################################
    
    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(hosts) - 1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            host = hosts[selected_row]
            username = usernames[selected_row]
            users = get_logged_in_users(host, username)
            services = get_running_services(host, username)
            display_info(stdscr, users, services)
        elif key == ord('q'):
            break

        display_menu(stdscr, hosts, selected_row)
        

        
def display_menu(stdscr, hosts, selected_row):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    ###################################################################
    ### ASCII art title adjusted in the middle of the screen
    ###################################################################

    title = [
    "___________                         .__",
    "\\__    ___/___   ____    ____  __ __|__|",
    "  |    |_/ __ \\ /    \\  / ___\\|  |  \\  |",
    "  |    |\\  ___/|   |  \\/ /_/  >  |  /  |",
    "  |____| \\___  >___|  /\\___  /|____/|__|",
    "             \\/     \\//_____/           "
]

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2
    for i, line in enumerate(title):
        stdscr.addstr(title_y + i, title_x, line)


    ###################################################################
    ### Displays the menu options which currently are host IP
    ### hosts file should contain IPs of desired hosts (IP per line)
    ### Displayed IPs are selectable and clickable
    ###################################################################
    for i, host in enumerate(hosts):
        x = w // 2 - len(host) // 2
        y = h // 2 - len(hosts) // 2 + i
        
        if i == selected_row:
            stdscr.addstr(y, x, host, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, host)

    stdscr.refresh()
    
    

def display_info(stdscr, users, services):

    ###################################################################
    ### Get user terminal max width and height to adjust TUI limits
    ###################################################################
    
    h, w = stdscr.getmaxyx()

    ###################################################################
    ### Splits information into an array of strings based on line breaks
    ###################################################################

    users_lines = users.splitlines()
    services_lines = services.splitlines()

    total_height = len(users_lines) + len(services_lines) + 9

    ###################################################################
    ### Initializes a scrollable pad for displaying information
    ###################################################################
    
    pad = curses.newpad(total_height, w)

    ###################################################################
    ### Tracking current position for user input actions
    ### pad_pos - topmost line that is currently seen in the pad
    ### selected_row - current line that user interacts with
    ###################################################################
    
    pad_pos = 0
    selected_row = 0
    
    while True:
        ###################################################################
        ### Clear the pad before each refresh
        ###################################################################
        
        pad.clear()

        ###################################################################
        ### Display users using get_logged_in_users() function
        ### Highlight line with curses.A_REVERSE if currently on that line
        ###################################################################
        
        pad.addstr(0, 0, f"Logged in users: {len(users_lines)}")
        for i, user in enumerate(users_lines, start=1):
            if i - 1 == selected_row:
                pad.addstr(i, 0, "[X]", curses.A_REVERSE)
                pad.addstr(i, 4, user, curses.A_REVERSE)
            else:
                pad.addstr(i, 0, "[X]")
                pad.addstr(i, 4, user)
        
        ###################################################################
        ### Display running services using get_running_services() function
        ### Highlight line with curses.A_REVERSE if currently on that line
        ### Truncate long service names if they exceed terminal width
        ###################################################################
        
        pad.addstr(len(users_lines) + 2, 0, f"Running services: {len(services_lines)}")
        for i, service in enumerate(services_lines, start=len(users_lines) + 3):
            if i - (len(users_lines) + 2) == selected_row:
                pad.addstr(i, 0, f"[X]{i}", curses.A_REVERSE)
                if len(service) > w - 4:
                    truncated_service = service[:w - 4]
                    pad.addstr(i, 5, truncated_service, curses.A_REVERSE)
                else:
                    pad.addstr(i, 5, service, curses.A_REVERSE)
            else:
                pad.addstr(i, 0, f"[X]{i}")
                if len(service) > w - 4: 
                    truncated_service = service[:w - 4]
                    pad.addstr(i, 5, truncated_service)
                else:
                    pad.addstr(i, 5, service)

        ###################################################################
        ### For test purposes, another field with selectable lines
        ### Currently selected_row works bad when jumping from services
        ###################################################################
        
        pad.addstr(len(users_lines) + len(services_lines) + 4, 0, "Hellos:")
        for i in range(len(users_lines) + len(services_lines) + 5, len(users_lines) + len(services_lines) + 7):
            if i - 3 == selected_row:
                pad.addstr(i, 0, f"[X]{i}", curses.A_REVERSE)
                pad.addstr(i, 6, "hello", curses.A_REVERSE)
            else:
                pad.addstr(i, 0, f"[X]{i}")
                pad.addstr(i, 6, "hello")

        ###################################################################
        ### Display footer
        ### Selected row, pad_pos and height are left for debugging purposes
        ###################################################################
        
        bottom_message = f"Press 'q' to go back to the main menu, selected row is {selected_row}, pad_pos =     {pad_pos}, h = {h}"
        stdscr.addstr(h-2, 0, bottom_message)

        ###################################################################
        ### Display the pad content on the screen
        ### Adjust height to fit in the terminal, leave space for footer
        ###################################################################
        
        pad.refresh(pad_pos, 0, 0, 0, h-3, w-1)

        ###################################################################
        ### Get user input
        ###################################################################
        
        key = stdscr.getch()
        if key == ord('q'):
            break
        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = selected_row
        elif key == curses.KEY_DOWN:
            selected_row = min(total_height, selected_row + 1)
            if selected_row >= pad_pos + h - 8:
                pad_pos = min(selected_row - h + 8, total_height - h)


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

def get_logged_in_users(host, username):
    command = f'ssh -o StrictHostKeyChecking=no {username}@{host} who'
    return execute_command(command)


def get_running_services(host, username):
    command = f'ssh -o StrictHostKeyChecking=yes {username}@{host} systemctl list-units --type=service --state=running | grep -v "LOAD   =" | grep -v "ACTIVE =" | grep -v "SUB    =" | grep -v "loaded units listed" | grep -v "^$"' 
    return execute_command(command)

if __name__ == "__main__":
    curses.wrapper(main)
