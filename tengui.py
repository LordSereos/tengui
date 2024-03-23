import curses
import subprocess

def main(stdscr):

    ###################################################################
    ### Setting up TUI:
    ### curs_set(0) disables the cursor
    ###################################################################
    
    curses.curs_set(0)

    ###################################################################
    ### Read from hosts file to retrieve desired hosts
    ### hosts file should be in the same directory as this script
    ###################################################################
    
    hosts = []
    usernames = []
    ports = []

    with open('hosts', 'r') as file:
        for line in file:
            # Split each line by whitespace
            parts = line.split()
            if len(parts) >= 2:
                # Extract IP and username
                ip_address = parts[0]
                port = parts[1]
                username = parts[2]
                hosts.append(ip_address)
                ports.append(port)
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
    ### Enter - enforces action on the current line (current_row)
    ### q     - used to go back or quit the TUI
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
            port = ports[selected_row]
            users = get_logged_in_users(host, port, username)
            services = get_running_services(host, port, username)
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

    total_height = len(users_lines) + len(services_lines) + 8

    ###################################################################
    ### Initializes a scrollable pad for displaying information
    ###################################################################
    
    pad = curses.newpad(total_height, w)
    

    ###################################################################
    ### Tracking current position for user input actions
    ### pad_pos      - topmost line that is currently seen in the pad
    ### selected_row - current line that user interacts with
    ###################################################################
    
    pad_pos = 0
    selected_row = 1
    
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
            if i == selected_row:
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
            if i - (len(users_lines) + 1) == selected_row:
                pad.addstr(i, 0, f"[X]", curses.A_REVERSE)
                if len(service) > w - 4:
                    truncated_service = service[:w - 4]
                    pad.addstr(i, 3, truncated_service, curses.A_REVERSE)
                else:
                    pad.addstr(i, 3, service, curses.A_REVERSE)
            else:
                pad.addstr(i, 0, f"[X]")
                if len(service) > w - 4: 
                    truncated_service = service[:w - 4]
                    pad.addstr(i, 3, truncated_service)
                else:
                    pad.addstr(i, 3, service)
        
        ###################################################################
        ### Display footer
        ### Selected row and onIt are left for debugging
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
        
        onIt = find_selected_element(selected_row, users_lines, services_lines)
        
        bottom_message = f"Press 'q' to go back to the main menu, selected row is {selected_row}, onIt = {onIt}"
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)

        ###################################################################
        ### Display the pad content on the screen
        ### Adjust height to fit in the terminal, leave space for footer
        ###################################################################
        pad.refresh(pad_pos, 0, 0, 0, h-3, w-1)

        ###################################################################
        ### Get user input:
        ### q     - go back to the main menu
        ### UP    - change the selected row to one higher if possible
        ### DOWN  - change the selected row to one lower if possible
        ### ENTER - open action confirmation modal
        ###################################################################
        
        key = stdscr.getch()
        if key == ord('q'):
            break
        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = selected_row
        elif key == curses.KEY_DOWN:
            selected_row = min((len(users_lines)+len(services_lines)), selected_row + 1)
            if selected_row >= pad_pos + h - 8:
                pad_pos = min(selected_row - h + 8, total_height - h)
        if key == curses.KEY_ENTER or key == 10:
            display_modal(stdscr, onIt, h, w)
            

def find_selected_element(selected_row, users_lines, services_lines):
    selected_element = ''
    if selected_row <= len(users_lines)+len(services_lines):
       if selected_row <= len(users_lines):
        selected_element = users_lines[selected_row-1]
       else:
        selected_element = services_lines[selected_row - len(users_lines)-1]
        
    return selected_element.split()[0]

    
def display_modal(stdscr, message, height, width):
    
    ###################################################################
    ### Center the modal, place it on top of the pad
    ### modal_y and modal_x represent the top-left corner coordinates
    ###################################################################
    
    center_y = height // 2
    center_x = width // 2
    
    modal_height = 10
    modal_width = width // 2
    
    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2
    
    ###################################################################
    ### Initialize the modal, add border to it.
    ### Initialize coloured pair to drag attention about an action.
    ###################################################################
    
    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()
    
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    
    modal.addstr(1, 2, f'KILLING {message} .', curses.color_pair(1))
    modal.addstr(3, 2, 'Are you sure?', curses.A_BOLD | curses.A_UNDERLINE)
    modal.addstr(7, 2, 'Press ENTER to confirm')
    modal.addstr(8, 2, 'Press q to cancel')
    modal.refresh()
    
    ###################################################################
    ### Get user input:
    ### ENTER - confirm action presented in the modal
    ### q     - close the modal
    ###################################################################
    while True:
        key = stdscr.getch()
        if key == curses.KEY_ENTER or key == 10:
            modal.addstr(5, 2, "SUCCESS", curses.A_BOLD)
            modal.refresh()
        elif key == ord('q'):
            break


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

def get_logged_in_users(host, port, username):
    command = f'ssh -o StrictHostKeyChecking=no -p {port} {username}@{host} who'
    return execute_command(command)


def get_running_services(host, port, username):
    command = f'ssh -o StrictHostKeyChecking=yes -p {port} {username}@{host} systemctl list-units --type=service --state=running | grep -v "LOAD   =" | grep -v "ACTIVE =" | grep -v "SUB    =" | grep -v "loaded units listed" | grep -v "^$" | grep -v "UNIT"' 
    return execute_command(command)
    
if __name__ == "__main__":
    curses.wrapper(main)

###################################################################
### Tengui TUI author:
### Martin Martijan
###################################################################
