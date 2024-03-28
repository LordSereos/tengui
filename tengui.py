import curses
import subprocess
import paramiko

def main(stdscr):

    ###################################################################
    ### Setting up TUI:
    ### curs_set(0) disables the cursor
    ###################################################################
    
    curses.curs_set(0)
    
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
    display_menu(stdscr, hosts, selected_row, title)
    
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
            if len(hosts) > 1:
                selected_row = min(len(hosts)-1, selected_row + 1)
            else:
                selected_row = min(len(hosts), selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_row == 0: 
                display_view_hosts_option(stdscr, hosts, ports, usernames, title)
            else:
                display_apply_scripts_option(stdscr, hosts, ports, usernames, title)
        elif key == ord('q'):
            break

        display_menu(stdscr, hosts, selected_row, title)
        

        
def display_menu(stdscr, hosts, selected_row, title):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2
    
    for i, line in enumerate(title):
        stdscr.addstr(title_y + i, title_x, line)

    bottom_message = f"Press 'q' to exit, {selected_row}"
    stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
    
    ###################################################################
    ### Displays the menu options which currently are host IP
    ### hosts file should contain IPs of desired hosts (IP per line)
    ### Displayed IPs are selectable and clickable
    ###################################################################
    
    menu_options = ["VIEW INDIVIDUAL HOSTS", "APPLY SCRIPTS"]
    for i, option in enumerate(menu_options):
        x = w // 2 - len(option) // 2
        y = h // 2 - len(menu_options) // 2 + i
        
        if i == selected_row:
            stdscr.addstr(y, x, option, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option)

    stdscr.refresh()
    
def display_view_hosts_option(stdscr, hosts, ports, usernames, title):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2
    
    for i, line in enumerate(title):
        stdscr.addstr(title_y + i, title_x, line)

    selected_row = 0
    bottom_message = f"Press 'q' to go back"
    stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
    
    ###################################################################
    ### Displays the menu options which currently are host IP
    ### hosts file should contain IPs of desired hosts (IP per line)
    ### Displayed IPs are selectable and clickable
    ###################################################################
    
    
            
    while True:
        for i, option in enumerate(hosts):
            x = w // 2 - len(option) // 2
            y = h // 2 - len(hosts) // 2 + i
        
            if i == selected_row:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)
        
        key = stdscr.getch()
        
        if i == selected_row:
            stdscr.addstr(y, x, option, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option)

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(hosts) - 1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            host = hosts[selected_row]
            username = usernames[selected_row]
            port = ports[selected_row]
            ports_info = get_port_info(host, port, username)
            display_info(stdscr, host, port, username)
        elif key == ord('q'):
            break

        stdscr.clear()  # Clearing the screen before redrawing
        
        for i, line in enumerate(title):
            stdscr.addstr(title_y + i, title_x, line)
     
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
        stdscr.refresh()
        
def display_apply_scripts_option(stdscr, hosts, ports, usernames, title):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2
    
    for i, line in enumerate(title):
        stdscr.addstr(title_y + i, title_x, line)

    selected_row = 0
    bottom_message = f"Press 'q' to go back (scripts1)"
    stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
    
    ###################################################################
    ### Displays the menu options which currently are host IP
    ### hosts file should contain IPs of desired hosts (IP per line)
    ### Displayed IPs are selectable and clickable
    ###################################################################
    
    while True:
        for i, option in enumerate(hosts):
            x = w // 2 - len(option) // 2
            y = h // 2 - len(hosts) // 2 + i
        
            if i == selected_row:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(hosts) - 1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            host = hosts[selected_row]
            username = usernames[selected_row]
            port = ports[selected_row]
            display_script_menu(stdscr, host, port, username)
        elif key == ord('q'):
            break

        stdscr.clear()  # Clearing the screen before redrawing
        for i, line in enumerate(title):
            stdscr.addstr(title_y + i, title_x, line)
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
        stdscr.refresh()
        
def display_script_menu(stdscr, host, port, username):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    selected_row = 1
    
    bottom_message = f"Press 'q' to go back (scripts menu)"
    stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
    
    check_ports_line = 1

    stdscr.addstr(check_ports_line, 0, "CHECK PORTS", curses.A_NORMAL) 
    if selected_row == check_ports_line:
        stdscr.addstr(check_ports_line, 0, "CHECK PORTS", curses.A_REVERSE)    

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(1, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            display_modal(stdscr, '', 'PORTS', h, w, host, port, username)
            pass
        elif key == ord('q'):
            break

        stdscr.refresh()  
    

def display_info(stdscr, host, port, username):

    ###################################################################
    ### Get user terminal max width and height to adjust TUI limits
    ###################################################################
    stdscr.refresh()
    h, w = stdscr.getmaxyx()
    
    users = get_logged_in_users(host, port, username)
    services = get_running_services(host, port, username)

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
        ### Highlight line with curses.A_REVERSE if currently on that line:
        ### (i-2) is for not counting header and empty line in between lists
        ### Truncate long service names if they exceed terminal width
        ###################################################################
        
        pad.addstr(len(users_lines) + 2, 0, f"Running services: {len(services_lines)}")
        for i, service in enumerate(services_lines, start=len(users_lines) + 3):
            if (i - 2) == selected_row:
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
        ### 
        ### POC menu-click initiated remote-shell-script with return to modal
        ### 
        ###################################################################
                    
        check_ports_line = len(users_lines) + len(services_lines) + 4

        pad.addstr(check_ports_line, 0, "CHECK PORTS", curses.A_NORMAL) 
        if selected_row == check_ports_line-4:
            pad.addstr(check_ports_line, 0, "[X] CHECK PORTS", curses.A_REVERSE) 




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
        
        onIt, family = find_selected_element(selected_row, users_lines, services_lines)
        
        bottom_message = f"Press 'q' to go back to the main menu, selected row is {selected_row}, onIt = {onIt.split()[0]+'                '} "
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
            selected_row = min((len(users_lines)+len(services_lines)+2), selected_row + 1)
            if selected_row >= pad_pos + h - 8:
                pad_pos = min(selected_row - h + 8, total_height - h)
        if key == curses.KEY_ENTER or key == 10:
            display_modal(stdscr, onIt, family, h, w, host, port, username)
            


def find_selected_element(selected_row, users_lines, services_lines):

    ###################################################################
    ### Mapping selected_row with real elements in lists, because when
    ### jumping we skip headers and empty lines
    ###
    ### selected_row-1 everywhere is because arrays starting index is 0,
    ### but selected_row starts from 1.
    ###################################################################
    
    selected_element = ''
    family = ''
    
    if selected_row <= len(users_lines)+len(services_lines)+4:
       if selected_row <= len(users_lines):
        selected_element = users_lines[selected_row-1]
        family = "USERS"
       elif selected_row <= len(users_lines)+len(services_lines):
        selected_element = services_lines[selected_row-len(users_lines)-1]
        family = "SERVICES"
       elif selected_row >= len(users_lines)+len(services_lines):
        selected_element = "CHECK PORTS"
        family = "PORTS"

    return selected_element, family 
    #return selected_element.split()[0]+"                     "
    
def display_modal(stdscr, onIt, family, height, width, host, port, username):
    
    ###################################################################
    ### Center the modal, place it on top of the pad
    ### modal_y and modal_x represent the top-left corner coordinates
    ###################################################################
    if onIt != '':
        who = onIt.split()[0]
    
    center_y = height // 2
    center_x = width // 2
    
    modal_height = 16
    modal_width = width -10
    
    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2
    
    ###################################################################
    ### Initialize the modal, add border to it.
    ### Initialize coloured pair to drag attention about an action.
    ###################################################################
    
    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()
    
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    if family == "USERS":
        withWhat = onIt.split()[1]
        modal.addstr(1, 2, f'KILLING USER {who} .', curses.color_pair(1))
        modal.addstr(3, 2, 'Are you sure?', curses.A_BOLD | curses.A_UNDERLINE)
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.addstr(10, 2, '')
        modal.refresh()
    elif family == "SERVICES":
        withWhat = onIt.split()[0]
        modal.addstr(1, 2, f'KILLING SERVICE {who} .', curses.color_pair(1))
        modal.addstr(3, 2, 'Are you sure?', curses.A_BOLD | curses.A_UNDERLINE)
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.addstr(10, 2, '')
        modal.refresh()
    elif family == "PORTS":
        modal.addstr(1, 2, "Enter separated by spaces ports that should be opened on the remote host: ")
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.refresh()
        
#       Get port numbers
        curses.echo()
        stdscr.move(modal_y + 4, modal_x + 2)
        port_input = stdscr.getstr().decode()
        curses.noecho() 
        ports = port_input.split(' ')
        
        get_port_info(host, port, username, *ports)
    
    
    ###################################################################
    ### Get user input:
    ### ENTER - confirm action presented in the modal
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
                #---------------------------------------------------------------------------------
                modal.addstr(5, 2, f"SUCCESS", curses.A_BOLD)
            modal.refresh()
        elif key == ord('q'):
            break

script_paths = {
    "check_ports": "./modules/ports/check.sh",
    "kill_service_by_name": "./modules/actions/kill_service_by_name.sh",
    "kill_login_session": "./modules/actions/kill_login_session.sh",
}

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

def run_shell_script(script_name, host, port, username, *args):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, port=port, username=username)

        if not ssh_client.get_transport().is_active():
            print("SSH connection is not alive.")
            return None

        script_path = script_paths.get(script_name)
        if script_path is None:
            print(f"Error: Script '{script_name}' not found.")
            return None

#        FOR EXECUTING REMOTE SCRIPT FROM REMOTE MACHINE
#        ------------------------------------------------
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

#       FOR EXECUTING REMOTE SCRIPT FROM LOCAL MACHINE
#        ------------------------------------------------
        with open(script_path, 'r') as file:
            script_content = file.read()

        command = f"sudo bash -s {' '.join(args)}"
        stdin, stdout, stderr = ssh_client.exec_command(command)

        stdin.write(script_content)
        stdin.channel.shutdown_write()

#       SAVE OUTPUT TO TEXR FILE
#        ------------------------------------------------

        output = stdout.read().decode()
        output_file_path = f"./{host}-{script_name}.info"
        with open(output_file_path, 'w') as output_file:
            output_file.write(output)
        return output
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        if ssh_client:
            ssh_client.close()


def get_logged_in_users(host, port, username):
    command = f'ssh -o StrictHostKeyChecking=yes -p {port} {username}@{host} who'
    return execute_command(command)

def get_running_services(host, port, username):
    command = f'ssh -o StrictHostKeyChecking=yes -p {port} {username}@{host} systemctl list-units --type=service --state=running | grep -v "LOAD   =" | grep -v "ACTIVE =" | grep -v "SUB    =" | grep -v "loaded units listed" | grep -v "^$" | grep -v "UNIT"' 
    return execute_command(command)
    
def get_port_info(host, port, username, *args):
    return run_shell_script("check_ports", host, port, username, *args)

if __name__ == "__main__":
    curses.wrapper(main)
