import curses
import subprocess
import paramiko

def main(stdscr):

    ###################################################################
    ### Setting up TUI:
    ### curs_set(0) disables the cursor.
    ###################################################################
    
    curses.curs_set(0)
    
    ###################################################################
    ### ASCII art title, will be used in several windows.
    ###################################################################
    
    title = [
    "___________                         .__",
    "\\__    ___/___   ____    ____  __ __|__|",
    "  |    |_/ __ \\ /    \\  / ___\\|  |  \\  |",
    "  |    |\\  ___/|   |  \\/ /_/  >  |  /  |",
    "  |____| \\___  >___|  /\\___  /|____/|__|",
    "             \\/     \\//_____/           "
    ]
    
    display_menu(stdscr, title)
       
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
    ### hosts - an array for host IP addresses.
    ### ports - an array for host ssh port number.
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
        ###################################################################
        
        for i, line in enumerate(title):
            stdscr.addstr(title_y + i, title_x, line)
            
        for i, option in enumerate(menu_options):
            x = w // 2 - len(option) // 2
            y = h // 2 - len(menu_options) // 2 + i
        
            if i == selected_row:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)
        
        ###################################################################
        ### bottom_message is used a footer which always will be displayed
        ### at the bottom of the screen. Reminds user of where he is or
        ### how to go back.
        ###################################################################
        
        bottom_message = f"Press 'q' to exit, {selected_row}"   
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
        
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
                display_view_hosts_option(stdscr, hosts, ports, usernames, title)
            else:
                display_apply_scripts_option(stdscr, hosts, ports, usernames, title)
        elif key == ord('q'):
            break
        stdscr.clear()
        stdscr.refresh()
    
def display_view_hosts_option(stdscr, hosts, ports, usernames, title):

    ###################################################################
    ### display_view_hosts_option() - secondary menu where user can
    ### view all hosts and select one for further inspection.
    ##################################################################

    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2
    
    selected_row = 0
  
    while True:
        for i, line in enumerate(title):
                stdscr.addstr(title_y + i, title_x, line)
                
        ###################################################################
        ### Menu items are previously extracted host IP addresses.
        ###################################################################  
          
        for i, option in enumerate(hosts):
            x = w // 2 - len(option) // 2
            y = h // 2 - len(hosts) // 2 + i
        
            if i == selected_row:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)
                 
        bottom_message = f"Press 'q' to go back to the main menu, {selected_row}"   
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
        
        ###################################################################
        ### When host is selected (ENTER is pressed), a new window will
        ### be displayed with information about that host.
        ################################################################### 
         
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(hosts) - 1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            host = hosts[selected_row]
            username = usernames[selected_row]
            port = ports[selected_row]
            display_info(stdscr, host, port, username)
        elif key == ord('q'):
            break

        stdscr.clear()
        stdscr.refresh()
        
def display_apply_scripts_option(stdscr, hosts, ports, usernames, title):

    ###################################################################
    ### display_apply_scripts_option() - secondary menu where user can
    ### view all hosts and select one or multiple to which to apply
    ### scripts or scans.
    ##################################################################
    
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title_x = w // 2 - len(title[0]) // 2
    title_y = 2

    selected_row = 0
    
    while True:
        for i, line in enumerate(title):
            stdscr.addstr(title_y + i, title_x, line)
            
        ###################################################################
        ### Menu items are previously extracted host IP addresses.
        ###################################################################
        
        for i, option in enumerate(hosts):
            x = w // 2 - len(option) // 2
            y = h // 2 - len(hosts) // 2 + i
        
            if i == selected_row:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)
                
        bottom_message = f"Press 'q' to go back to main menu, {selected_row}"
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
        
        ###################################################################
        ### When host is selected (ENTER is pressed), a new window will
        ### be displayed with a list of scripts to be run on that host.
        ###
        ### Currently doesn't support multiple host selection.
        ################################################################### 
        
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

    ###################################################################
    ### Splits information into an array of strings based on line breaks.
    ###################################################################

    users_lines = users.splitlines()
    services_lines = services.splitlines()
    
    ###################################################################
    ### Total amount of selectable elements is going to be the sum
    ### of all elements of different information lists plus unintended
    ### lines which include empty lines and headers to show what kind 
    ### of information is presented below.
    ###################################################################
    
    unintented_lines = 8
    total_height = len(users_lines) + len(services_lines) + unintented_lines

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

    while True:
        ###################################################################
        ### Clear the pad before each refresh.
        ###################################################################
    
        pad.clear()

        ###################################################################
        ### Display users using get_logged_in_users() function.
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
        ### Display running services using get_running_services() function.
        ###
        ### (i-2) is for not counting header and empty line in between lists
        ### Truncate long service names if they exceed terminal width.
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
        
        onIt, family = find_selected_element_in_host_info(selected_row, users_lines, services_lines)
        
        bottom_message = f"Press 'q' to go back to the main menu, selected row is {selected_row}, onIt = {onIt.split()[0]+'                '} "
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)

        ###################################################################
        ### Display the pad content on the screen.
        ### Adjust height to fit in the terminal, leave space for footer.
        ###################################################################
        
        pad.refresh(pad_pos, 0, 0, 0, h-3, w-1)

        ###################################################################
        ### Get user input:
        ### q     - go back to the main menu.
        ### UP    - change the selected row to one higher if possible.
        ### DOWN  - change the selected row to one lower if possible.
        ### ENTER - open action confirmation modal.
        ###################################################################
        
        key = stdscr.getch()
        if key == ord('q'):
            break
        if key == curses.KEY_UP:
            selected_row = max(1, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = selected_row
        elif key == curses.KEY_DOWN:
            selected_row = min((len(users_lines)+len(services_lines)), selected_row + 1)
            if selected_row >= pad_pos + h - 8:
                pad_pos = min(selected_row - h + 8, total_height - h)
        if key == curses.KEY_ENTER or key == 10:
            confirmation_modal(stdscr, onIt, family, h, w, host, port, username)
            
def find_selected_element_in_host_info(selected_row, users_lines, services_lines):

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
    modal_width = width -10
    
    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2
    
    ###################################################################
    ### Initialize the modal, add border to it.
    ### Initialize coloured pair to use different colouring for some
    ### text in the modal to drag attention.
    ###################################################################
    
    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()
    
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    
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
        modal.addstr(1, 2, f'KILLING USER {who} .', curses.color_pair(1))
        modal.addstr(3, 2, 'Are you sure?', curses.A_BOLD | curses.A_UNDERLINE)
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.addstr(10, 2, '')
        modal.refresh()
    if family == "SERVICES":
        withWhat = onIt.split()[0]
        modal.addstr(1, 2, f'KILLING SERVICE {who} .', curses.color_pair(1))
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
        
def display_script_menu(stdscr, host, port, username):

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
    
    selected_row = 3
    
    ###################################################################
    ### script_lines - an array with the names of the scripts that
    ### can be chosen. Will grow when new modules are added.
    ###
    ### script_x - an array containing x axis information of where to
    ### place corresponding menu option. The rows are incrementory 
    ### by 2 so that they are not close together (for greater appeal).
    ###################################################################
    
    script_lines = ["CHECK PORTS", "MAKE BACKUPS", "RUN LYNIS SCAN"]
    script_x = [3, 5, 7]
      
    ###################################################################
    ### Displaying menu options, highlighting when current row matches.
    ###
    ### When ENTER is pressed for the current row, a modal will appear
    ### to guide user for further actions. Depending on which script
    ### is to run, a modal with different parameters will open.
    ###################################################################
    while True:
        stdscr.addstr(1, 2, "Selected host amount to apply scripts: 1", curses.A_NORMAL) 
        stdscr.addstr(script_x[0], w // 2 - len(script_lines[0]) // 2, script_lines[0], curses.A_NORMAL) 
        stdscr.addstr(script_x[1], w // 2 - len(script_lines[1]) // 2, script_lines[1], curses.A_NORMAL) 
        stdscr.addstr(script_x[2], w // 2 - len(script_lines[2]) // 2, script_lines[2], curses.A_NORMAL) 
        
        if selected_row == script_x[0]:
            stdscr.addstr(script_x[0], w // 2 - len(script_lines[0]) // 2, script_lines[0], curses.A_REVERSE)
        if selected_row == script_x[1]:
            stdscr.addstr(script_x[1], w // 2 - len(script_lines[1]) // 2, script_lines[1], curses.A_REVERSE)
        if selected_row == script_x[2]:
            stdscr.addstr(script_x[2], w // 2 - len(script_lines[2]) // 2, script_lines[2], curses.A_REVERSE)  
        
        bottom_message = f"Press 'q' to go back to all hosts, {selected_row}"
        stdscr.addstr(h-2, 0, bottom_message, curses.A_BOLD)
        
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(3, selected_row - 2)
        elif key == curses.KEY_DOWN:
            selected_row = min(7, selected_row + 2)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_row == script_x[0]:
                script_menu_modal(stdscr, 'PORTS', h, w, host, port, username)
            if selected_row == script_x[1]:
                script_menu_modal(stdscr, 'BACKUP', h, w, host, port, username)
            if selected_row == script_x[2]:
                script_menu_modal(stdscr, 'LYNIS', h, w, host, port, username)
        elif key == ord('q'):
            break

        stdscr.clear()
        stdscr.refresh()

def script_menu_modal(stdscr, family, height, width, host, port, username):
    
    ###################################################################
    ### script_menu_modal() - modal which will be called when some
    ### kind of confirmation or guidance is needed to proceed with
    ### the selected script to apply to host(s).
    ##################################################################

    center_y = height // 2
    center_x = width // 2
    
    modal_height = 16
    modal_width = width -10
    
    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2
   
    
    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()
    
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    
    ###################################################################
    ### Depending on for which script this modal is, it will add
    ### different content to it.
    ###
    ### 'family' is the parameter to name which script to run, it
    ### is determined based on which row the user was when ENTER was
    ### pressed in the script menu.
    ###################################################################
    
    if family == "PORTS":
        modal.addstr(1, 2, "Enter ports separated by spaces that should be opened on the remote host")
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
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
        ### curses.scho() - enables character echoing, what is typed is 
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
                ports = port_input.split()
                get_port_info(host, port, username, *ports)
                modal.addstr(5, 2, f"SUCCESS", curses.A_BOLD)
                modal.addstr(8, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif is_numeric_char(key):
                port_input += chr(key)  # Append numeric character to port_input
        
    ###################################################################
    ### for BACKUP and LYNIS connection with back end script logic 
    ### is NOT IMPLEMENTED YET.
    ###################################################################
    
    if family == "BACKUP":
        modal.addstr(1, 2, "Initiating backup script. ")
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.refresh()
        
        while True:        
            key = stdscr.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                pass
            elif key == ord('q'):
                break
                
    if family == "LYNIS":
        modal.addstr(1, 2, "Initiating Lynis scan.")
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.refresh()

        while True:        
            key = stdscr.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                pass
            elif key == ord('q'):
                break


script_paths = {
    "check_ports": "./modules/ports/check.sh",
    "kill_service_by_name": "./modules/actions/kill_service_by_name.sh",
    "kill_login_session": "./modules/actions/kill_login_session.sh",
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
        print("Error:", e)
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
