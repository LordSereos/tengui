import subprocess
import threading
import paramiko
import concurrent.futures
import logging
import time
import io
import os


logging.basicConfig(
    filename='debug.log',  # Log file
    level=logging.WARNING,  # Log level (DEBUG to capture all details)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    filemode='w'  # Overwrite the log file each time the script runs
)


script_paths = {
    "check_ports": "./modules/ports/check.sh",
    "kill_service_by_name": "./modules/actions/kill_service_by_name.sh",
    "kill_login_session": "./modules/actions/kill_login_session.sh",
    "get_currently_opened_ports": "./modules/ports/check_currently_opened_ports.sh",
    "hasher": "./modules/hasher/hasher.sh",
}


def get_elements_for_ip(ip_address, element):
    ###################################################################
    ### get_elements_for_ip is a function to retrieve necessary
    ### information (element) about the provided host (ip_address) from
    ### our documentation file (doc_file).
    ###
    ### It first finds the line in which provided IP is present, then
    ### starts looking for the line where provided element is present.
    ### After that it retrieves the data from an array and returns
    ### them.
    ###################################################################
    with open("doc_file", 'r') as file:
        found_ip = False
        for line in file:
            if found_ip:
                # We found the line with the IP address on the previous iteration,
                # so we need to search for the desired element in subsequent lines
                if element + ':' in line:
                    elements_str = line.split(':')[1].strip()
                    elements = elements_str[1:-1].split(',')
                    return [elem.strip() for elem in elements]
            if ip_address in line:
                found_ip = True
    # If the loop completes without finding the desired element, return None
    return None


def set_window_param(stdscr):
    ###################################################################
    ### Get parameters of opened tab of the terminal.
    ### Used for displaying information dynamically according to the
    ### size of the window. Title will always be displayed in the top
    ### middle of each menu screen.
    ###
    ### TO DO: If terminal dimension are small, don't show title.
    ###################################################################
    h, w = stdscr.getmaxyx()

    # title_x = w // 2 - len(title[0]) // 2
    upper_y = 0

    return h, w, upper_y, 0


def set_current_unintended(h, host_counts):
    unintended_lines = 0
    intended_lines = 0
    for i in range(h):
        if host_counts[i]+4 + intended_lines + unintended_lines >= h:
            break

        intended_lines += host_counts[i]
        unintended_lines += 4

    return intended_lines, unintended_lines


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
        output_file_path = f"./modules/ports/outputs/{host}-{script_name}.info"
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


def get_lastb_output(host):
    file_path = f"./modules/audit/{host}/lastb.log"

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Remove the last 2 lines which are empty
        filtered_lines = lines[:-2]
        last_5_lines = filtered_lines[:10]

        # logging.warning(f"Last 5 lines (after removing last 2) are: {last_5_lines}")
        return last_5_lines
    else:
        raise FileNotFoundError(f"Log file {file_path} does not exist.")


def get_manifest_output(host):
    file_path = f"./modules/hasher/{host}/changelog"

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        if not lines:
            return ["Nothing here..."]

        filtered_lines = [line for line in lines if '/.' not in line]
        last_lines = filtered_lines[-10:]

        logging.warning(f"LAST 10 OF MANIFEST (without hidden paths): {last_lines}")
        return last_lines
    else:
        return ["Nothing here."]


def get_checked_ports(host):
    file_path = f"./modules/ports/outputs/{host}-check_ports.info"
    if os.path.exists(file_path):

        with open(file_path, 'r') as file:
            lines = file.readlines()

        logging.warning(f"Checked ports lines: {lines}")
        return lines
    else:
        return ["You haven't run CHECK PORTS script for this host."]

def get_port_info(hosts, ports, usernames, *args):
    # print(args)
    for i, _ in enumerate(hosts):
        run_shell_script("check_ports", hosts[i-1], ports[i-1], usernames[i-1], *args[i-1])
    return 0


def run_concrete_script(script_path, hosts, ports, usernames, *folders):
    commands = []

    if isinstance(hosts, str):
        hosts = [hosts]
    if isinstance(ports, str):
        ports = [ports]
    if isinstance(usernames, str):
        usernames = [usernames]

    for i, _ in enumerate(hosts):
        command = f"{script_path} {usernames[i]} {hosts[i]} {ports[i]} {folders[i]} > /dev/null 2>&1"
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
        command = f"./modules/lynisCan/lynis.sh {usernames[i - 1]} {hosts[i - 1]} {ports[i - 1]} > /dev/null 2>&1 &"
        commands.append(command)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_command, cmd) for cmd in commands]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"ERROR: {e}")

    return 0

# SINGLY COMMENTED IN THIS BLOCK IS AN APPROACH OF RUNNING MULTIPLE HOSTS ONE AFTER ANOTHER
# DOUBLY COMMENTED IS THE PREVIOUS APPROACH OF RUNNING ONE HOST, AS PER PREVIOUS SINGULAR MENU OPTION
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

# RUNNING ALL HOSTS CONCURRENTLY


# Global variables to track host statuses
host_status = {}
previous_status = {}
stop_threads = False


def is_host_alive(host_ip):
    """Ping the host to check if it's alive or unreachable."""
    try:
        response = subprocess.run(['ping', '-c', '1', '-W', '1', host_ip],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        return response.returncode == 0  # Return True if alive, False otherwise
    except Exception as e:
        logging.error(f"Error pinging {host_ip}: {e}")  # Error log
        return False


def ping_host_in_background(host_ip):
    """Thread function to ping host and update status."""
    global host_status, previous_status
    status = is_host_alive(host_ip)
    new_status = "ALIVE" if status else "UNREACHABLE"

    if host_ip in previous_status and previous_status[host_ip] != new_status:
        # Log status change
        logging.debug(f"STATUS {host_ip}: {previous_status[host_ip]} -> {new_status}")

    # Update the current status and previous status dictionaries
    host_status[host_ip] = new_status
    previous_status[host_ip] = new_status
    #logging.debug(f"Updated {host_ip} status to {new_status}")  # Log current update


def start_ping_checks(host_ips):
    """Start background ping checks for all hosts."""
    for ip in host_ips:
        # Start a thread for each host to ping in the background
        thread = threading.Thread(target=ping_host_in_background, args=(ip,))
        thread.daemon = True  # Mark as daemon so it doesn't block the program from exiting
        thread.start()
        #logging.debug(f"Started pinging thread for {ip}")  # Debugging log


def repeated_ping(host_ips, interval=30):
    """Ping hosts every 'interval' seconds."""
    global stop_threads
    while not stop_threads:  # Continue only if stop_threads is False
        start_ping_checks(host_ips)
        time.sleep(interval)


def ssh_connect(host, port, username):
    """Establish an SSH connection."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=username)
    return ssh


def execute_command2(ssh, command):
    """Execute a command on the remote host and return the output."""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode() + stderr.read().decode()


def interactive_shell(stdscr, host, port, username, curses):
    """Simulate an interactive shell session with the remote host."""
    ssh = ssh_connect(host, port, username)

    center_y = stdscr.getmaxyx()[0] // 2
    center_x = stdscr.getmaxyx()[1] // 2

    modal_height = 20
    modal_width = stdscr.getmaxyx()[1] - 10

    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2

    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()

    # Create a pad for scrolling output
    pad_height = 200  # Total height of pad
    pad_width = modal_width - 2
    output_pad = curses.newpad(pad_height, pad_width)

    modal.addstr(1, 2, "Interactive remote shell. Type your commands below.")
    modal.addstr(2, 2, 'Press ENTER to execute, q to quit.')

    modal.refresh()

    current_y = 0  # Track the current line position in the pad
    view_y = 0     # Track the visible part of the pad
    command = ''   # Initialize command

    while True:
        # Draw the command input line
        modal.addstr(modal_height - 2, 2, 'Command: ')
        modal.addstr(modal_height - 2, 10, command + ' ' * (modal_width - 10 - len(command)))
        modal.refresh()

        key = modal.getch()

        # Handle ENTER key to execute the command
        if key == curses.KEY_ENTER or key in [10, 13]:
            if command:
                try:
                    output = execute_command2(ssh, command)
                    # logging.warning(f"Output of {command}: {output}")
                    output_lines = output.splitlines()

                    # Add new output to the pad
                    for line in output_lines:
                        if current_y < pad_height:
                            output_pad.addstr(current_y, 0, line)
                            current_y += 1
                        else:
                            # Scroll up to make space for new lines
                            output_pad.scroll(-1)
                            output_pad.addstr(pad_height - 1, 0, line)  # Add line at the bottom

                    # Adjust view_y if necessary to ensure last output is visible
                    if current_y > (view_y + (modal_height - 5)):
                        view_y = max(0, current_y - (modal_height - 5))

                    # Update the visible part of the pad
                    output_pad.refresh(view_y, 0, modal_y + 3, modal_x + 1, modal_y + modal_height - 3,
                                       modal_x + modal_width - 1)

                    command = ''  # Clear command after execution

                except Exception as e:
                    error_message = f"Error: {e}"
                    if current_y < pad_height:
                        output_pad.addstr(current_y, 0, error_message)
                        current_y += 1
                    else:
                        output_pad.scroll(-1)
                        output_pad.addstr(pad_height - 1, 0, error_message)

                    # Adjust view_y if necessary to ensure error message is visible
                    if current_y > (view_y + (modal_height - 4)):
                        view_y = max(0, current_y - (modal_height - 4))

                    # Update the visible part of the pad
                    output_pad.refresh(view_y, 0, modal_y + 3, modal_x + 1, modal_y + modal_height - 3,
                                       modal_x + modal_width - 1)

        # Handle 'q' key to quit
        elif key == 20:  # Detect Ctrl+Q
            break

        # Handle backspace for removing last character in command
        elif key == curses.KEY_BACKSPACE or key == 127:
            command = command[:-1]

        # Handle scrolling with arrow keys (up and down)
        elif key == curses.KEY_UP:
            if view_y > 0:  # Prevent scrolling beyond the top
                view_y -= 1
                output_pad.refresh(view_y, 0, modal_y + 3, modal_x + 1, modal_y + modal_height - 3,
                                   modal_x + modal_width - 1)

        elif key == curses.KEY_DOWN:
            if view_y + (modal_height - 4) < current_y:  # Prevent scrolling beyond the bottom
                view_y += 1
                output_pad.refresh(view_y, 0, modal_y + 3, modal_x + 1, modal_y + modal_height - 3,
                                   modal_x + modal_width - 1)

        # Handle escape sequences (arrow keys and other special keys)
        elif key == 27:  # Escape sequence
            key2 = modal.getch()  # Get the second part of the escape sequence
            if key2 == 91:  # Escape sequence for arrow keys
                key3 = modal.getch()  # Get the final part of the escape sequence
                if key3 == 65:  # Arrow Up
                    if view_y > 0:  # Prevent scrolling beyond the top
                        view_y -= 1
                        output_pad.refresh(view_y, 0, modal_y + 3, modal_x + 1, modal_y + modal_height - 3,
                                           modal_x + modal_width - 1)
                elif key3 == 66:  # Arrow Down
                    if view_y + (modal_height - 5) < current_y:  # Prevent scrolling beyond the bottom
                        view_y += 1
                        output_pad.refresh(view_y, 0, modal_y + 3, modal_x + 1, modal_y + modal_height - 3,
                                           modal_x + modal_width - 1)

        # Handle printable character input for the command, excluding escape sequences
        elif 32 <= key <= 126:  # Only allow printable ASCII characters
            command += chr(key)

    ssh.close()


def execute_generic_script(family, host_ips, host_ports, host_usernames):

    doc_ports = []
    doc_locations = []
    doc_manifests = []
    doc_chkrootkit = []
    doc_audit = []

    host_ips = [host_ips] if isinstance(host_ips, str) else host_ips

    logging.warning(f"host_ips: {host_ips}")

    for i, host in enumerate(host_ips):
        logging.warning(f"{i} iteration {host}")
        doc_ports.append(get_elements_for_ip(host, "ports"))
        doc_locations.append(get_elements_for_ip(host, "copy_locations"))
        doc_manifests.append(get_elements_for_ip(host, "manifest_dirs"))
        doc_chkrootkit.append(get_elements_for_ip(host, "chkrootkit"))
        doc_audit.append(get_elements_for_ip(host, "audit_dirs"))

    # logging.warning(f"doc_ports: {doc_ports}")

    if family == "SETUP AUDIT":
        run_concrete_script("./modules/audit/setup.sh", host_ips, host_ports, host_usernames, *doc_locations)
    if family == "MAKE BACKUP":
        run_concrete_script("./modules/backup/backupFiles.sh", host_ips, host_ports, host_usernames, *doc_locations)
    if family == "CHECK PORTS":
        get_port_info(host_ips, host_ports, host_usernames, *doc_ports)
    if family == "MANIFEST":
        logging.warning(f"Manifest location: {doc_manifests}")
        run_concrete_script("./modules/hasher/hasher.sh", host_ips, host_ports, host_usernames, *doc_locations)
    if family == "CHECK ROOTKIT":
        run_concrete_script("./modules/chkrootkit/rootkit.sh", host_ips, host_ports, host_usernames, *doc_locations)













