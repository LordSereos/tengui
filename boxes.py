import functions
import logging

def display_menu_box4(pad, start_y, w, menu_options, header, curses, selected_row, host_counts, k, i, selected_hosts):
    # Calculate box dimensions
    box_start_x = (w - (2 * w // 3)) // 2  # Centered horizontally
    box_end_x = 2 * w // 3
    box_height = len(menu_options) + 4  # Add some padding for header/footer

    # Draw the box within the pad (allow drawing outside visible area)
    pad.attron(curses.color_pair(1))
    pad.hline(start_y, box_start_x, curses.ACS_HLINE, box_end_x)
    pad.hline(start_y + box_height - 1, box_start_x, curses.ACS_HLINE, box_end_x)
    pad.vline(start_y + 1, box_start_x, curses.ACS_VLINE, box_height - 2)
    pad.vline(start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE, box_height - 2)

    # Draw corners
    pad.addch(start_y, box_start_x, curses.ACS_ULCORNER)
    pad.addch(start_y + box_height - 1, box_start_x, curses.ACS_LLCORNER)
    pad.addch(start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
    pad.addch(start_y + box_height - 1, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

    # Display header
    header_x = box_start_x + 2
    pad.addstr(start_y, header_x, header, curses.A_ITALIC | curses.color_pair(1))
    pad.attroff(curses.color_pair(1))


    # Display each menu option
    for j, option in enumerate(menu_options):
        x = box_start_x + ((2 * w // 3) - len(option)) // 2  # Centered horizontally
        y = start_y + j + 2

        if option in functions.host_status:
            if functions.host_status[option] == "ALIVE":
                indicator = " [UP]  "
                color_pair = curses.color_pair(2)  # Green color for alive
            else:
                indicator = " [DOWN]"
                color_pair = curses.color_pair(3)  # Red color for unreachable
        else:
            indicator = " [...]"
            color_pair = curses.color_pair(1)  # Default color for checking

            # Display the option (host IP) and the indicator
        if i == selected_row:
            if i in selected_hosts:
                pad.addstr(y, x, f"{option}", curses.color_pair(4) | curses.A_REVERSE)  # Highlight selected row
                pad.addstr(y, x + len(option), indicator, curses.A_REVERSE | color_pair)
            else:
                pad.addstr(y, x, f"{option}", curses.A_REVERSE)  # Highlight selected row
                pad.addstr(y, x + len(option), indicator, curses.A_REVERSE | color_pair)
        else:
            if i in selected_hosts:
                pad.addstr(y, x, f"{option}", curses.color_pair(4))
                pad.addstr(y, x + len(option), indicator, color_pair)
            else:
                pad.addstr(y, x, f"{option}")
                pad.addstr(y, x + len(option), indicator, color_pair)

        i += 1


def display_title_box(title, title_y, title_x, stdscr, curses):
    for i, line in enumerate(title):
        stdscr.addstr(title_y + i, title_x, line, curses.color_pair(1))


def display_footer_box(text, h, stdscr, curses):
    ###################################################################
    ### footer_message is used as a footer which will always be
    ### displayed at the bottom of the screen. Reminds user of useful
    ### commands or how to open context menu (if applicable).
    ###################################################################
    footer_message = text
    stdscr.addstr(h - 2, 1, footer_message, curses.A_DIM | curses.A_ITALIC)


def display_pad_box(pad, text, curses, section_start, ection_end, w):
    pad.attron(curses.color_pair(1))
    pad.hline(section_start, 0, curses.ACS_HLINE, w)
    pad.hline(ection_end, 0, curses.ACS_HLINE, w)
    pad.vline(section_start + 1, 0, curses.ACS_VLINE, ection_end - section_start - 1)
    pad.vline(section_start + 1, w - 1, curses.ACS_VLINE, ection_end - section_start - 1)
    pad.addch(section_start, 0, curses.ACS_ULCORNER)
    pad.addch(section_start, w - 1, curses.ACS_URCORNER)
    pad.addch(ection_end, 0, curses.ACS_LLCORNER)
    pad.addch(ection_end, w - 1, curses.ACS_LRCORNER)
    pad.addstr(section_start, 2, text, curses.A_ITALIC | curses.color_pair(1))
    # pad.addstr(section_start, w - 2 - len(line), line, curses.A_ITALIC | curses.color_pair(1))
    pad.attroff(curses.color_pair(1))


def display_help_modal(pad, pad_pos, curses):
    modal_width = 45
    modal_height = 14
    modal_text = ("Context information:"
                  "\n\nSPACE - scroll whole page down"
                  "\ny / Y - scroll whole page up\ng / G - scroll to next info tab"
                  "\nb / B - scroll to previous info tab\ns / S - open interactive shell"
                  "\nCtr+t - exit interactive shell\nu / U - explicitly setup audit\n"
                  "\nq / Q - go back to host list\nh / H - close context menu")
    # Calculate the position to draw the modal (top-right corner)
    modal_y = pad_pos + 1
    modal_x = pad.getmaxyx()[1] - modal_width - 1

    for y in range(modal_y, modal_y + modal_height):
        pad.addstr(y, modal_x, ' ' * modal_width)

    # Create a window for the modal
    modal_win = pad.subpad(modal_height, modal_width, modal_y, modal_x)

    # Clear the area behind the modal

    # Draw the box for the modal
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    modal_win.attron(curses.color_pair(5))
    modal_win.box()

    # Add the modal text inside the box
    modal_text_lines = modal_text.split('\n')
    for i, line in enumerate(modal_text_lines):
        if i == 0:  # Skip applying bold to the first line
            modal_win.addstr(i + 1, 1, line[:modal_width - 2].ljust(modal_width - 2))
        else:
            prefix = line[:5]
            suffix = line[5:]
            # Apply bold attribute to the prefix
            modal_win.addstr(i + 1, 1, prefix, curses.A_BOLD | curses.color_pair(5))
            # Add the remaining part of the line without bold attribute
            modal_win.addstr(suffix)
    modal_win.attroff(curses.color_pair(5))


def display_confirmation_modal(onIt, family, height, width, host, port, username, stdscr, curses):
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
    modal_width = width - 10

    modal_y = center_y - modal_height // 2
    modal_x = center_x - modal_width // 2

    ###################################################################
    ### Initialize the modal, add border to it.
    ### Initialize coloured pair to use different colouring for some
    ### text in the modal to drag attention.
    ###################################################################

    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()

    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

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
        modal.addstr(1, 2, f'KILLING USER {who} .', curses.color_pair(3))
        modal.addstr(3, 2, 'Are you sure?', curses.A_BOLD | curses.A_UNDERLINE)
        modal.addstr(7, 2, 'Press ENTER to confirm')
        modal.addstr(8, 2, 'Press q to cancel')
        modal.addstr(10, 2, '')
        modal.refresh()
    if family == "SERVICES":
        withWhat = onIt.split()[0]
        modal.addstr(1, 2, f'KILLING SERVICE {who} .', curses.color_pair(3))
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
                functions.run_shell_script("kill_login_session", host, port, username, withWhat)
                modal.addstr(5, 2, f"SUCCESS", curses.A_BOLD)
            if family == "SERVICES":
                functions.run_shell_script("kill_service_by_name", host, port, username, withWhat)
                modal.addstr(5, 2, f"SUCCESS", curses.A_BOLD)
            modal.refresh()
        elif key == ord('q'):
            break


def display_script_menu(host_info, curses, stdscr):

    host_ips = [host[0] for host in host_info]
    host_ports = [host[1] for host in host_info]
    host_usernames = [host[2] for host in host_info]

    max_y, max_x = stdscr.getmaxyx()

    modal_height = 15
    modal_width = 40

    modal_y = (max_y - modal_height) // 2
    modal_x = (max_x - modal_width) // 2

    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.border()
    modal.attron(curses.color_pair(5))
    modal.box()
    modal.refresh()
    modal.keypad(True)

    script_options = ["SETUP AUDIT", "MAKE BACKUP", "CHECK PORTS", "MANIFEST", "CHECK ROOTKIT"]

    selected_row = 0

    while True:
        modal.refresh()

        for i, option in enumerate(script_options):
            option_x = (modal_width - len(option)) // 2  # Center the text horizontally
            if selected_row == i:
                modal.addstr(i + 2, option_x, option, curses.A_BOLD | curses.color_pair(5) | curses.A_REVERSE)
            else:
                modal.addstr(i + 2, option_x, option, curses.A_BOLD | curses.color_pair(5))

        # modal.addstr(modal_height-2, 1, f"{host_ips}", curses.A_DIM | curses.A_ITALIC)

        key = modal.getch()

        if key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(script_options)-1, selected_row + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            modal.addstr(modal_height - 4, 1, " "*(modal_width-3))
            modal.addstr(modal_height - 4, 1, f"Executing {script_options[selected_row]}, please wait. ",)
            modal.addstr(modal_height - 3, 1, " "*(modal_width-3))
            modal.refresh()
            functions.execute_generic_script(script_options[selected_row], host_ips, host_ports, host_usernames)
            modal.addstr(modal_height - 3, 1, f"{script_options[selected_row]} executed!", curses.A_DIM | curses.A_ITALIC)
            modal.refresh()
        elif key == ord('q'):
            break


