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
        footer_message = f"selected_row: {selected_row}"
        stdscr.addstr(h - 2, 1, footer_message, curses.A_DIM | curses.A_ITALIC)
        footer_message2 = f"pad_pos: {pad_pos}"
        stdscr.addstr(h - 1, 1, footer_message2, curses.A_DIM | curses.A_ITALIC)
        footer_message3 = f"h: {h}"
        stdscr.addstr(h - 3, 1, footer_message3, curses.A_DIM | curses.A_ITALIC)
        footer_message5 = f"hosts: {total_hosts}"
        stdscr.addstr(h - 5, 1, footer_message5, curses.A_DIM | curses.A_ITALIC)
        footer_message6 = f"selected: {selected_hosts}"
        stdscr.addstr(h - 6, 1, footer_message6, curses.A_DIM | curses.A_ITALIC)
        footer_message7 = f"unintended_lines: {unintended_lines}"
        stdscr.addstr(h - 7, 1, footer_message7, curses.A_DIM | curses.A_ITALIC)
        footer_message8 = f"intended_lines: {intended_lines}"
        stdscr.addstr(h - 8, 1, footer_message8, curses.A_DIM | curses.A_ITALIC)


        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = max(0, selected_row)
        elif key == curses.KEY_DOWN:
            selected_row = min(total_hosts-1, selected_row + 1)
            if selected_row >= intended_lines:
                pad_pos = min(selected_row, total_hosts - len(host_counts)*4)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_hosts:
                for index in selected_hosts:
                    if 0 <= index < len(flattened_hosts):  # Ensure index is valid
                        host, port, username = flattened_hosts[index]
                        logging.debug(f"Selected Host - IP: {host}, Port: {port}, Username: {username}")
                    else:
                        logging.warning(f"Index {index} is out of range in flattened_hosts.")
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
        elif key == ord('q'):
            global stop_threads
            stop_threads = True
            break


def display_info(stdscr, host, port, username):
    stdscr.clear()
    stdscr.refresh()
    h, w, upper_y, selected_row = functions.set_window_param(stdscr)

    ###################################################################
    ### Get information about logged in users and running services
    ### on that host.
    ###################################################################

    users = functions.get_logged_in_users(host, port, username)
    services = functions.get_running_services(host, port, username)
    ports = functions.get_currently_opened_ports(host, port, username)

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

        stdscr.addstr(h - 3, 0, " " * w)
        boxes.display_footer_box(f"Press 'h' to open context menu                               ", h, stdscr, curses)

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
            selected_row = min((len(users_lines) + len(services_lines) + len(ports_lines)), selected_row + 1)
            if selected_row >= pad_pos + h - unintented_lines:
                pad_pos = min(selected_row - h + unintented_lines, total_height - h)
        elif key == ord(' '):
            selected_row = min((len(users_lines) + len(services_lines) + len(ports_lines)), pad_pos + h - 3)
            pad_pos = min(total_height - h, h)
        elif key == ord('y') or key == ord('Y'):
            selected_row = max(1, selected_row - h)
            if selected_row <= pad_pos:
                pad_pos = max(0, selected_row - 1)
        elif key == ord('g') or key == ord('G'):
            # Jump to the next family list
            if family == "USERS":
                selected_row = min((len(users_lines) + len(services_lines) + len(ports_lines)), len(users_lines) + 1)
            if family == "SERVICES":
                selected_row = min((len(users_lines) + len(services_lines) + len(ports_lines)),
                                   len(users_lines) + len(services_lines) + 1)
            if selected_row >= pad_pos + h - 6:
                pad_pos = min(selected_row - h + 8, selected_row + 3)
        elif key == ord('b') or key == ord('B'):
            # Jump to the previous family list
            if family == "SERVICES":
                selected_row = 1
            if family == "PORTS":
                selected_row = len(users_lines) + 1
            if selected_row <= pad_pos:
                pad_pos = max(0, selected_row - 1)
        elif key == ord('h'):
            modal_visible = not modal_visible
        elif key == ord('u'):
            TODO: Open execute command modal fromm boxes.script_menu_modal
        elif key == curses.KEY_ENTER or key == 10:
            boxes.display_confirmation_modal(onIt, family, h, w, host, port, username, stdscr, curses)
        elif key == ord('q'):
            break


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

    if selected_row <= len(users_lines) + len(services_lines) + len(ports_lines) + 6:
        if selected_row <= len(users_lines):
            selected_element = users_lines[selected_row - 1]
            family = "USERS"
        elif selected_row <= len(users_lines) + len(services_lines):
            selected_element = services_lines[selected_row - len(users_lines) - 1]
            family = "SERVICES"
        elif selected_row >= len(users_lines) + len(services_lines):
            selected_element = ports_lines[selected_row - len(users_lines) - len(services_lines) - 1]
            family = "PORTS"

    return selected_element, family


def display_script_menu(stdscr, title, hosts, usernames, ports):
    ###################################################################
    ### display_script_menu() - final menu where user can view and
    ### select scripts or scans which are to be run on the selected
    ### host.
    ###################################################################

    stdscr.clear()
    h, w, title_x, title_y, selected_row = functions.set_window_param(stdscr, title)

    ###################################################################
    ### selected_row is initiated from 3 becase we want to leave some
    ### space at the top to display how many hosts are we applying the
    ### scripts to.
    ###
    ### We will not be able to jump to lesser rows.
    ###################################################################

    selected_row = title_y + len(title) + 4

    ###################################################################
    ### script_lines - an array with the names of the scripts that
    ### can be chosen. Will grow when new modules are added.
    ###
    ### script_x - an array containing x axis information of where to
    ### place corresponding menu option. The rows are incrementory
    ### by 2 so that they are not close together (for greater appeal).
    ###################################################################

    script_lines = ['PORTS', 'BACKUP', 'LYNIS', 'MANIFEST', 'CHKROOTKIT', 'AUDIT_SETUP', 'AUDIT_RETRIEVE',
                    'CUSTOM_COMMAND']
    script_x = [title_y + len(title) + 4 + i for i in range(len(script_lines))]

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

        boxes.display_title_box(title, title_y, title_x, stdscr, curses)
        boxes.display_menu_box(title, title_y, w, script_lines, "Script menu", stdscr, curses, selected_row, 4)

        bottom_message = f"Press 'q' to go back to all hosts"
        stdscr.addstr(h - 2, 1, f"Selected hosts: {hosts}", curses.A_ITALIC | curses.A_DIM)
        stdscr.addstr(h - 3, 1, bottom_message, curses.A_ITALIC | curses.A_DIM)

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(title_y + len(title) + 4, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(title_y + len(title) + 11, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            for i, option in enumerate(script_lines):
                if selected_row == script_x[i]:
                    boxes.script_menu_modal(stdscr, option, h, w, hosts, ports, usernames, doc_ports, doc_locations,
                                            doc_manifests, doc_chkrootkit, doc_audit, curses)
                    break
        elif key == ord('q'):
            break

        stdscr.clear()
        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
