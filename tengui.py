import curses
import subprocess

PASSWORD = "87654321"  # Password for SSH connections

def display_menu(stdscr, hosts, selected_row):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # ASCII art title
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


    # Print the menu options
    for i, host in enumerate(hosts):
        x = w // 2 - len(host) // 2
        y = h // 2 - len(hosts) // 2 + i
        
        # Highlight the selected row
        if i == selected_row:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, host, curses.A_REVERSE)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, host)

    stdscr.refresh()

def execute_command(command):
    try:
        # Execute the command and capture the output
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        # Handle errors (if any)
        return f"Error: {e.output}"

def get_logged_in_users(host):
    command = f'sshpass -p "{PASSWORD}" ssh -o StrictHostKeyChecking=no martin@{host} who'
    return execute_command(command)

def get_running_services(host):
    command = f'sshpass -p "{PASSWORD}" ssh -o StrictHostKeyChecking=no martin@{host} systemctl list-units --type=service --state=running | grep -v "LOAD   =" | grep -v "ACTIVE =" | grep -v "SUB    =" | grep -v "loaded units listed" | grep -v "^$"' 
    return execute_command(command)

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    with open('hosts', 'r') as file:
        hosts = file.read().splitlines()

    selected_row = 0
    display_menu(stdscr, hosts, selected_row)

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(hosts) - 1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            host = hosts[selected_row]
            users = get_logged_in_users(host)
            services = get_running_services(host)
            display_info(stdscr, users, services)
        elif key == ord('q'):
            break

        display_menu(stdscr, hosts, selected_row)

def display_info(stdscr, users, services):
    h, w = stdscr.getmaxyx()

    users_lines = users.splitlines()
    services_lines = services.splitlines()

    total_height = len(users_lines) + len(services_lines) + 9

    pad = curses.newpad(total_height, w)

    pad_pos = 0
    selected_row = 0
    
    while True:
        # Clear the pad before each refresh
        pad.clear()

        # Display users
        pad.addstr(0, 0, f"Logged in users: {len(users_lines)}")
        for i, user in enumerate(users_lines, start=1):
            if i - 1 == selected_row:
                pad.addstr(i, 0, "[X]", curses.A_REVERSE)
                pad.addstr(i, 4, user, curses.A_REVERSE)
            else:
                pad.addstr(i, 0, "[X]")
                pad.addstr(i, 4, user)
        
        # Display services
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

        pad.addstr(len(users_lines) + len(services_lines) + 4, 0, "Hellos:")
        for i in range(len(users_lines) + len(services_lines) + 5, len(users_lines) + len(services_lines) + 7):
            if i - 3 == selected_row:
                pad.addstr(i, 0, f"[X]{i}", curses.A_REVERSE)
                pad.addstr(i, 6, "hello", curses.A_REVERSE)
            else:
                pad.addstr(i, 0, f"[X]{i}")
                pad.addstr(i, 6, "hello")

        # Display footer
        bottom_message = f"Press 'q' to go back to the main menu, selected row is {selected_row}, pad_pos = {pad_pos}, h = {h}"
        stdscr.addstr(h-2, 0, bottom_message)

        # Display the pad content on the screen
        pad.refresh(pad_pos, 0, 0, 0, h-3, w-1)  # Adjust height to fit in the terminal, leave space for footer

        # Get user input
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


def display_info2(stdscr, users, services):
    h, w = stdscr.getmaxyx()

    users_lines = users.splitlines()
    services_lines = services.splitlines()

    show_services = True
    total_height_users = len(users_lines)
    total_height_services = len(services_lines) if show_services else 0 
    total_height = total_height_users + total_height_services + 9

    pad = curses.newpad(total_height, w)

    pad_pos = 0
    selected_row = 0
    

    while True:
        # Clear the pad before each refresh
        pad.clear()
        total_height_services = len(services_lines) if show_services else 0 
        # Display users
        pad.addstr(0, 0, f"Logged in users: {total_height_users}")
        for i, user in enumerate(users_lines, start=1):
            # Highlight the selected row
            if i - 1 == selected_row:
                pad.addstr(i, 0, "[X]", curses.A_REVERSE)
                pad.addstr(i, 4, user, curses.A_REVERSE)
            else:
                pad.addstr(i, 0, "[X]")
                pad.addstr(i, 4, user)
        
        # Display services
        pad.addstr(len(users_lines) + 2, 0, f"Running services: {len(services_lines)}")
        if show_services:
            for i, service in enumerate(services_lines, start=len(users_lines) + 3):
                # Highlight the selected row
                if i - (len(users_lines) + 2) == selected_row:
                    pad.addstr(i, 0, "[X]", curses.A_REVERSE)
                    if len(service) > w - 4:  # Check if service description exceeds terminal width
                        # Truncate long descriptions and add horizontal scrolling
                        truncated_service = service[:w - 4]
                        pad.addstr(i, 5, truncated_service, curses.A_REVERSE)
                    else:
                        pad.addstr(i, 5, service, curses.A_REVERSE)
                else:
                    pad.addstr(i, 0, "[X]")
                    if len(service) > w - 4:  # Check if service description exceeds terminal width
                        # Truncate long descriptions and add horizontal scrolling
                        truncated_service = service[:w - 4]
                        pad.addstr(i, 5, truncated_service)
                    else:
                        pad.addstr(i, 5, service)

        pad.addstr(total_height_users + total_height_services + 4, 0, f"Line after services: {len(services_lines)}")
        for i in range(total_height_users + total_height_services + 5, total_height_users + total_height_services + 7):
            if i - 1 == selected_row:
                pad.addstr(i, 0, "[X]", curses.A_REVERSE)
                pad.addstr(i, 4, "hello", curses.A_REVERSE)
            else:
                pad.addstr(i, 0, "[X]")
                pad.addstr(i, 4, "hello")

        # Display bottom message
        bottom_message = f"Press 'q' to go back to the main menu, selected row is {selected_row}"
        info = f"thu = {total_height_users}, ths = {total_height_services}"
        stdscr.addstr(h-2, 0, bottom_message)
        stdscr.addstr(h-1, 0, info)

        # Display the pad content on the screen
        pad.refresh(pad_pos, 0, 0, 0, h-3, w-1)  # Adjust height to fit in the terminal, leave space for footer

        # Get user input
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('h'):
            show_services = not show_services
            pad_pos = 0
            selected_row = 0
        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
            if selected_row < pad_pos:
                pad_pos = selected_row
        elif key == curses.KEY_DOWN:
            selected_row = min(total_height, selected_row + 1)
            if selected_row >= pad_pos + h - 8:
                pad_pos = min(selected_row - h + 8, total_height - h)


if __name__ == "__main__":
    curses.wrapper(main)
