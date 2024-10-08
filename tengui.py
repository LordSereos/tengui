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



if __name__ == "__main__":
    curses.wrapper(main)
