import curses
import subprocess
import paramiko
import functions
import boxes
import concurrent.futures
import threading
import logging

def main(stdscr):

    curses.curs_set(0)

    title2 = [
        "░███████████                     ░████  ░███░████ ",
        "░   ░███  ██████ ████████   ██████░███   ░██ ░███ ",
        "    ░███ ███░███░░███░░███ ███░░██░███   ░██ ░███ ",
        "    ░███░███░░░  ░███ ░███░███ ░██░███   ░██ ░███ ",
        "    ████░░██████ ████ ████░░██████░█████████ ░███",
        "   ░░░░░ ░░░░░░ ░░░░ ░░░░░ ░░░░░██░░░░░░░░░░  ░░░ ",
        "                            ██████                "
    ]
    title = [
        "TengUI"
    ]
    display_menu(stdscr)


def display_menu(stdscr):

    h, w, upper_y, selected_row = functions.set_window_param(stdscr)

    groups = {}
    current_group = None
    host_counts = []  # Initialize an empty list to store counts
    current_count = 0


    with open('hosts', 'r') as file:
        for line in file:
            line = line.strip()  # Remove any leading/trailing whitespace
            if line.startswith('-'):  # Check for group name
                if current_count > 0:
                    # Save the count for the previous group
                    host_counts.append(current_count)
                    # Reset current_count for the new group
                current_count = 0
                current_group = line[1:]  # Get the group name without the leading '-'
                groups[current_group] = []  # Initialize an empty list for the new group
            else:
                parts = line.split()
                if len(parts) >= 3 and current_group:  # Ensure it's a valid host line and there's a group
                    ip_address = parts[0]
                    port = parts[1]
                    username = parts[2]
                    groups[current_group].append((ip_address, port, username))
                    current_count += 1

        # Don't forget to add the count for the last group after finishing the file
        if current_group is not None:
            host_counts.append(len(groups[current_group]))

    all_hosts = [(group, host[0]) for group, hosts in groups.items() for host in hosts]
    total_hosts = len(all_hosts)

    host_ips = []
    for hosts in groups.values():
        host_ips.extend([host[0] for host in hosts])
    # functions.repeated_ping(host_ips)
    ping_thread = threading.Thread(target=functions.repeated_ping, args=(host_ips, 10))
    ping_thread.daemon = True  # Set as daemon so it exits when the main program exits
    ping_thread.start()

    selected_row = 0  # Index of the selected host in the current group
    pad_pos = 0  # Current scroll position in the pad (in rows)

    pad_height = total_hosts+len(host_counts)*5 # Ensure pad is at least as tall as needed
    pad_width = w
    pad = curses.newpad(pad_height, pad_width)

    # Flatten the groups into a single list of all hosts
    flattened_hosts = []
    for group, hosts in groups.items():
        flattened_hosts.extend(hosts)

    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green for alive
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

    selected_hosts = set()

    while True:

        stdscr.clear()
        stdscr.refresh()

        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        content_start_y = 1
        current_host_index = 0

        i = 0
        k = 0
        for group_name, hosts in groups.items():
            menu_options = [host[0] for host in hosts]  # Extract IP addresses
            host_count = len(menu_options)  # Number of hosts in this group

            boxes.display_menu_box4(
                pad, content_start_y, w, menu_options, f"{group_name}",
                curses, selected_row, host_counts, k, i, selected_hosts)

            content_start_y += host_count + 3 + 2  # Move start_y for the next group
            current_host_index += host_count  # Update index for the next group# Move start_y for next group
            i += host_counts[k]
            k += 1

        pad.refresh(pad_pos, 0, 0, 0, h - 1, w - 1)

        intended_lines, unintended_lines = functions.set_current_unintended(h, host_counts)
        # footer_message = f"selected_row: {selected_row}"
        # stdscr.addstr(h - 2, 1, footer_message, curses.A_DIM | curses.A_ITALIC)
        # footer_message2 = f"pad_pos: {pad_pos}"
        # stdscr.addstr(h - 1, 1, footer_message2, curses.A_DIM | curses.A_ITALIC)
        # footer_message3 = f"h: {h}"
        # stdscr.addstr(h - 3, 1, footer_message3, curses.A_DIM | curses.A_ITALIC)
        # footer_message5 = f"hosts: {total_hosts}"
        # stdscr.addstr(h - 5, 1, footer_message5, curses.A_DIM | curses.A_ITALIC)
        # footer_message6 = f"selected: {selected_hosts}"
        # stdscr.addstr(h - 6, 1, footer_message6, curses.A_DIM | curses.A_ITALIC)
        # footer_message7 = f"unintended_lines: {unintended_lines}"
        # stdscr.addstr(h - 7, 1, footer_message7, curses.A_DIM | curses.A_ITALIC)
        # footer_message8 = f"intended_lines: {intended_lines}"
        # stdscr.addstr(h - 8, 1, footer_message8, curses.A_DIM | curses.A_ITALIC)


        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = max(0, selected_row)
        elif key == curses.KEY_DOWN:
            selected_row = min(total_hosts-1, selected_row + 1)
            if selected_row >= intended_lines:
                pad_pos = min(selected_row,total_hosts + len(host_counts)*4+len(host_counts)*2-h)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_hosts:
                host_info = []
                for index in selected_hosts:
                    if 0 <= index < len(flattened_hosts):  # Ensure index is valid
                        host_info.append(flattened_hosts[index])
                        host, port, username = flattened_hosts[index]
                        i += 1
                        # logging.warning(f"Selected Host - IP: {host}, Port: {port}, Username: {username}")
                    else:
                        logging.warning(f"Index {index} is out of range in flattened_hosts.")

                # logging.warning(f"selected_hosts: {selected_hosts}")
                # logging.warning(f"flattened_hosts: {host_info}")
                boxes.display_script_menu(host_info, curses, stdscr)

            else:
                host, port, username = flattened_hosts[selected_row]
                display_info(stdscr, host, port, username)
        elif key == ord('g') or key == ord('G'):
            if len(selected_hosts) == len(host_ips):
                selected_hosts.clear()
            else:
                selected_hosts = set(range(len(host_ips)))
        elif key == ord('t') or key == ord('T'):
            if selected_row in selected_hosts:
                selected_hosts.remove(selected_row)
            else:
                selected_hosts.add(selected_row)
        elif key == ord('q') or key == 20:
            global stop_threads
            stop_threads = True
            break


def display_info(stdscr, host, port, username):
    stdscr.clear()
    stdscr.refresh()
    h, w, upper_y, selected_row = functions.set_window_param(stdscr)

    functions.run_concrete_script("./modules/audit/retrieve.sh", host, port, username, "")
    functions.execute_generic_script("MANIFEST", host, port, username)

    ###################################################################
    ### Get information about logged in users and running services
    ### on that host.
    ###################################################################

    users = functions.get_logged_in_users(host, port, username)
    services = functions.get_running_services(host, port, username)
    ports = functions.get_currently_opened_ports(host, port, username)
    lastb = functions.get_lastb_output(host)
    manifest = functions.get_manifest_output(host)
    checked_ports = functions.get_checked_ports(host)

    ###################################################################
    ### Splits information into an array of strings based on line breaks.
    ###################################################################

    users_lines = users.splitlines()
    services_lines = services.splitlines()
    ports_lines = ports.splitlines()
    lastb_lines = [line.strip() for line in lastb if line.strip()]
    manifest_lines = [line.strip() for line in manifest if line.strip()]
    checked_ports_lines = [line.strip() for line in checked_ports if line.strip()]


    # logging.warning(f"Length of lastb: {len(lastb_lines)}")
    # logging.warning(f"manifest_Lines: {manifest_lines}")
    logging.warning(f"checked_ports_lines: {checked_ports_lines}")


    ###################################################################
    ### Total amount of selectable elements is going to be the sum
    ### of all elements of different information lists plus unintended
    ### lines which include empty lines and headers to show what kind 
    ### of information is presented below.
    ###################################################################

    unintented_lines = 14 + 1
    total_height = (len(users_lines) + len(services_lines) + len(ports_lines)
                    + len(lastb_lines) + len(manifest_lines) + len(checked_ports_lines)
                    + unintented_lines)

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
        pad.clear()

        users_section_start = 0
        users_section_end = len(users_lines) + 1

        boxes.display_pad_box(pad, f"Logged-in users ({len(users_lines)})", curses, users_section_start,
                              users_section_end, w)

        # Add the users information inside the border
        for i, line in enumerate(users_lines, start=1):
            if i == selected_row:
                pad.addstr(i, 1, "[X]", curses.A_REVERSE)
                pad.addstr(i, 5, line, curses.A_REVERSE)
            else:
                pad.addstr(i, 1, "[X]")
                pad.addstr(i, 5, line)

        ###################################################################
        ### Display running services using get_running_services() function.
        ###
        ### (i-2) is for not counting header and empty line in between lists
        ### Truncate long service names if they exceed terminal width.
        ###################################################################

        services_section_start = users_section_end + 1
        services_section_end = services_section_start + len(services_lines) + 1

        boxes.display_pad_box(pad, f"Running services ({len(services_lines)})", curses, services_section_start,
                              services_section_end, w)

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

        boxes.display_pad_box(pad, f"Currently opened ports ({len(ports_lines)})", curses, ports_section_start,
                              ports_section_end, w)

        for i, port_info in enumerate(ports_lines, start=len(services_lines) + len(users_lines) + 5):
            if (i - 4) == selected_row:
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

        checked_ports_lines_start = len(users_lines) + len(services_lines) + len(ports_lines) + 6
        checked_ports_lines_end = checked_ports_lines_start + len(checked_ports_lines) + 1

        boxes.display_pad_box(pad, f"Documented ports", curses, checked_ports_lines_start,
                              checked_ports_lines_end, w)

        for i, checked_ports_info in enumerate(checked_ports_lines, start=checked_ports_lines_start + 1):
            if (i - 6) == selected_row:
                if len(checked_ports_info) > w - 5:
                    truncated_port = checked_ports_info[:w - 5]
                    pad.addstr(i, 2, truncated_port, curses.A_REVERSE)
                else:
                    pad.addstr(i, 2, checked_ports_info, curses.A_REVERSE)
            else:
                if len(checked_ports_info) > w - 5:
                    truncated_port = checked_ports_info[:w - 5]
                    pad.addstr(i, 2, truncated_port)
                else:
                    pad.addstr(i, 2, checked_ports_info)

        lastb_section_start = len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines) + 8
        lastb_section_end = lastb_section_start + len(lastb_lines) + 1

        boxes.display_pad_box(pad, f"Last unsuccessful logins", curses, lastb_section_start,
                              lastb_section_end, w)

        for i, lastb_info in enumerate(lastb_lines, start=lastb_section_start + 1):
            if (i - 8) == selected_row:
                if len(lastb_info) > w - 5:
                    truncated_port = lastb_info[:w - 5]
                    pad.addstr(i, 2, truncated_port, curses.A_REVERSE)
                else:
                    pad.addstr(i, 2, lastb_info, curses.A_REVERSE)
            else:
                if len(lastb_info) > w - 5:
                    truncated_port = lastb_info[:w - 5]
                    pad.addstr(i, 2, truncated_port)
                else:
                    pad.addstr(i, 2, lastb_info)

        manifest_section_start = len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines) + len(lastb_lines) + 10
        manifest_section_end = manifest_section_start + len(manifest_lines) + 1

        boxes.display_pad_box(pad, f"Changed files", curses, manifest_section_start,
                              manifest_section_end, w)

        for i, manifest_info in enumerate(manifest_lines, start=manifest_section_start + 1):
            if (i - 10) == selected_row:
                if len(manifest_info) > w - 5:
                    truncated_port = manifest_info[:w - 5]
                    pad.addstr(i, 2, truncated_port, curses.A_REVERSE)
                else:
                    pad.addstr(i, 2, manifest_info, curses.A_REVERSE)
            else:
                if len(manifest_info) > w - 5:
                    truncated_port = manifest_info[:w - 5]
                    pad.addstr(i, 2, truncated_port)
                else:
                    pad.addstr(i, 2, manifest_info)



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

        onIt, family = find_selected_element_in_host_info(selected_row, users_lines,
                services_lines, ports_lines, lastb_lines, manifest_lines, checked_ports_lines)

        stdscr.addstr(h - 3, 0, " " * w)
        boxes.display_footer_box(f"Press 'h' to open context menu                               ", h, stdscr, curses)
        # bottom_message = (f"Selected row is {selected_row}, {len(checked_ports_lines)} onIt = {onIt.split()[0]+ '  ' + family+ ' '*10 } ")
        # stdscr.addstr(h - 1, 0, bottom_message)

        ###################################################################
        ### Display the pad content on the screen.
        ### Adjust height to fit in the terminal, leave space for footer.
        ###################################################################
        if modal_visible:
            boxes.display_help_modal(pad, pad_pos, curses)
        pad.refresh(pad_pos, 0, 0, 0, h - 3, w - 1)

        ###################################################################
        ### Get user input:
        ### q     - go back to the main menu.
        ### UP    - change the selected row to one higher if possible.
        ### DOWN  - change the selected row to one lower if possible.
        ### ENTER - open action confirmation modal.
        ###################################################################

        # pad_unintented_lines = h - shown_info

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(1, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = selected_row - 1
        elif key == curses.KEY_DOWN:
            selected_row = min(total_height-unintented_lines, selected_row + 1)
            if selected_row >= pad_pos + h - unintented_lines:
                pad_pos = min(selected_row - h + unintented_lines, total_height - h)
        elif key == ord(' '):
            selected_row = min(total_height-unintented_lines, pad_pos + h - 3)
            pad_pos = min(total_height - h, pad_pos+h)
        elif key == ord('y') or key == ord('Y'):
            selected_row = max(1, selected_row - h)
            if selected_row <= pad_pos:
                pad_pos = max(0, selected_row - 1)
        elif key == ord('g') or key == ord('G'):
            # Jump to the next family list
            if family == "USERS":
                selected_row = len(users_lines) + 1
            if family == "SERVICES":
                selected_row = len(users_lines) + len(services_lines) + 1
            if family == "PORTS":
                selected_row = len(users_lines) + len(services_lines) + len(ports_lines) + 1
            if family == "CHECKED_PORTS":
                selected_row = len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines) + 1
            if family == "LASTB":
                selected_row = len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines) + len(lastb_lines) + 1
            if selected_row >= pad_pos + h - h/2:
                pad_pos = min(total_height - h, selected_row + 3)
        elif key == ord('b') or key == ord('B'):
            # Jump to the previous family list
            if family == "SERVICES":
                selected_row = 1
            if family == "PORTS":
                selected_row = len(users_lines) + 1
            if family == "CHECKED_PORTS":
                selected_row = len(users_lines) + len(services_lines) + 1
            if family == "LASTB":
                selected_row = len(users_lines) + len(services_lines) + len(ports_lines) + 1
            if family == "MANIFEST":
                selected_row = len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines)+ 1
            if selected_row <= pad_pos:
                pad_pos = max(0, selected_row - 1)
        elif key == ord('h'):
            modal_visible = not modal_visible
        elif key == ord('u'):
            functions.run_audit_retrieve_script(host, port, username)
        elif key == ord('s'):
            functions.interactive_shell(stdscr, host, port, username, curses)
        elif key == curses.KEY_ENTER or key == 10:
            boxes.display_confirmation_modal(onIt, family, h, w, host, port, username, stdscr, curses)
        elif key == ord('q'):
            break


def find_selected_element_in_host_info(selected_row, users_lines, services_lines, ports_lines, lastb_lines, manifest_lines, checked_ports_lines):
    ###################################################################
    ### Mapping selected_row with real elements in lists, because when
    ### jumping we skip headers and empty lines
    ###
    ### selected_row-1 everywhere is because arrays starting index is 0,
    ### but selected_row starts from 1.
    ###################################################################

    selected_element = 'UNDEFINED'
    family = ''

    if selected_row <= len(users_lines) + len(services_lines) + len(ports_lines) + len(lastb_lines) + 8:
        if selected_row <= len(users_lines):
            selected_element = users_lines[selected_row - 1]
            family = "USERS"
        elif selected_row <= len(users_lines) + len(services_lines):
            selected_element = services_lines[selected_row - len(users_lines) - 1]
            family = "SERVICES"
        elif selected_row <= len(users_lines) + len(services_lines) + len(ports_lines):
            selected_element = ports_lines[selected_row - len(users_lines) - len(services_lines) - 1]
            family = "PORTS"
        elif selected_row <= len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines):
            selected_element = checked_ports_lines[selected_row - len(users_lines) - len(services_lines) - len(ports_lines) - 1]
            family = "CHECKED_PORTS"
        elif selected_row <= len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines) + len(lastb_lines):
            selected_element = lastb_lines[selected_row - len(users_lines) - len(services_lines) - len(ports_lines) - len(checked_ports_lines) - 1]
            family = "LASTB"
        elif selected_row > len(users_lines) + len(services_lines) + len(ports_lines) + len(checked_ports_lines) + len(lastb_lines):
            selected_element = manifest_lines[selected_row - len(users_lines) - len(services_lines) - len(ports_lines) - len(checked_ports_lines) - len(lastb_lines) - 1]
            family = "MANIFEST"
        # elif selected_row > len(users_lines) + len(services_lines) + len(ports_lines) + len(lastb_lines) + len(manifest_lines):
        #     selected_element = checked_ports_lines[selected_row - len(users_lines) - len(services_lines) - len(ports_lines) - len(lastb_lines) - len(manifest_lines)-1]
        #     family = "CHECKED_PORTS"

    return selected_element, family


<<<<<<< HEAD
=======
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
>>>>>>> 53d222fd469a9101818b13ef19abed29a3392f93

if __name__ == "__main__":
    curses.wrapper(main)
