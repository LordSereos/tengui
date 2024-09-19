import subprocess
import threading
import paramiko
import concurrent.futures
import logging

logging.basicConfig(
    filename='debug.log',  # Log file
    level=logging.DEBUG,  # Log level (DEBUG to capture all details)
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
        folders_str = ' '.join(folders[i - 1])
        command = f"./modules/backup/backupFiles.sh {usernames[i - 1]} {hosts[i - 1]} {ports[i - 1]} {folders_str} > /dev/null 2>&1"
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


def run_manifest_script(hosts, ports, usernames, *folders):
    commands = []
    for i, _ in enumerate(hosts):
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
        folders_str = ' '.join(folders[i])
        command = f"./modules/chkrootkit/rootkit.sh {usernames[i]} {hosts[i]} {ports[i]} {folders_str} > /dev/null 2>&1"
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


host_status = {}


def is_host_alive(host_ip):
    """Ping the host to check if it's alive or unreachable."""
    try:
        logging.debug(f"Pinging {host_ip}...")  # Debugging log
        response = subprocess.run(['ping', '-c', '1', '-W', '1', host_ip],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        if response.returncode == 0:
            logging.debug(f"{host_ip} is ALIVE")  # Debugging log
            return True  # Host is alive
        else:
            logging.debug(f"{host_ip} is UNREACHABLE")  # Debugging log
            return False  # Host is unreachable
    except Exception as e:
        logging.error(f"Error pinging {host_ip}: {e}")  # Error log
        return False  # If any exception occurs, consider the host unreachable


def ping_host_in_background(host_ip):
    """Thread function to ping host and update status."""
    status = is_host_alive(host_ip)
    host_status[host_ip] = "ALIVE" if status else "UNREACHABLE"
    logging.debug(f"Updated {host_ip} status to {host_status[host_ip]}")  # Debugging log


def start_ping_checks(host_ips):
    """Start background ping checks for all hosts."""
    for ip in host_ips:
        # Start a thread for each host to ping in the background
        thread = threading.Thread(target=ping_host_in_background, args=(ip,))
        thread.daemon = True  # Mark as daemon so it doesn't block the program from exiting
        thread.start()
        logging.debug(f"Started pinging thread for {ip}")  # Debugging log


import time


# Function to ping hosts and repeat every 30 seconds
def repeated_ping(host_ips, interval=10):
    """Ping hosts every 'interval' seconds."""
    start_ping_checks(host_ips)
    threading.Timer(interval, repeated_ping, [host_ips, interval]).start()