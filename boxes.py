import functions


def display_menu_box(title, title_y, w, menu_options, header, stdscr, curses, selected_row, type, isReadOnly=False, selected_hosts=None):

    box_start_y = title_y + len(title) + 2
    box_end_y = box_start_y + len(menu_options) + 3
    box_start_x = (w - (2 * w // 3)) // 2  # (Centered horizontally)
    box_end_x = 2 * w // 3

    stdscr.attron(curses.color_pair(1))
    stdscr.hline(box_start_y, box_start_x, curses.ACS_HLINE, box_end_x)
    stdscr.hline(box_end_y, box_start_x, curses.ACS_HLINE, box_end_x)
    stdscr.vline(box_start_y + 1, box_start_x, curses.ACS_VLINE, box_end_y - box_start_y - 1)
    stdscr.vline(box_start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE, box_end_y - box_start_y - 1)

    stdscr.addch(box_start_y, box_start_x, curses.ACS_ULCORNER)
    stdscr.addch(box_start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
    stdscr.addch(box_end_y, box_start_x, curses.ACS_LLCORNER)
    stdscr.addch(box_end_y, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

    header_text = header
    header_x = box_start_x + 2
    stdscr.addstr(box_start_y, header_x, header_text, curses.A_ITALIC | curses.color_pair(1))
    stdscr.attroff(curses.color_pair(1))

    # Display each menu option
    for i, option in enumerate(menu_options):
        x = box_start_x + ((2 * w // 3) - len(option)) // 2  # (Centered horizontally)
        y = box_start_y + i + 2

        if i == selected_row:
            stdscr.addstr(y, x, option, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option)


def display_menu_box2(title, title_y, w, menu_options, header, stdscr, curses, selected_row, type, isReadOnly=False, selected_hosts=None):

    box_start_y = title_y + len(title) + 2
    box_end_y = box_start_y + len(menu_options) + 3
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

    header_text = header
    header_x = box_start_x + 2
    stdscr.addstr(box_start_y, header_x, header_text, curses.A_ITALIC | curses.color_pair(1))
    stdscr.attroff(curses.color_pair(1))

    ###################################################################
    ### type 1: for main menu options
    ### type 2: for IP host group names (Administrators, Users, ...)
    ### type 3: for list of IP addresses in a group
    ### type 4: display script menu
    ###################################################################
    if type == 1:
        main_menu_options(menu_options, box_start_x, box_start_y, w, selected_row, stdscr, curses)
    if type == 2:
        groups_menu_options(menu_options, box_start_x, box_start_y, w, selected_row, stdscr, curses)
    if type == 3:
        host_group_options(menu_options, box_start_x, box_start_y, w, selected_row, stdscr, curses, isReadOnly, selected_hosts)
    if type == 4:
        script_menu_options(menu_options, title_y, title, w, selected_row, stdscr, curses)


def display_menu_box3(pad, title, start_y, w, menu_options, header, curses, selected_row):
    box_start_x = (w - (2 * w // 3)) // 2  # Centered horizontally
    box_end_x = 2 * w // 3

    # Draw box
    pad.attron(curses.color_pair(1))
    pad.hline(start_y, box_start_x, curses.ACS_HLINE, box_end_x)
    pad.hline(start_y + len(menu_options) + 3, box_start_x, curses.ACS_HLINE, box_end_x)
    pad.vline(start_y + 1, box_start_x, curses.ACS_VLINE, len(menu_options) + 2)
    pad.vline(start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE, len(menu_options) + 2)

    pad.addch(start_y, box_start_x, curses.ACS_ULCORNER)
    pad.addch(start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
    pad.addch(start_y + len(menu_options) + 3, box_start_x, curses.ACS_LLCORNER)
    pad.addch(start_y + len(menu_options) + 3, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

    # Display header
    header_x = box_start_x + 2
    pad.addstr(start_y, header_x, header, curses.A_ITALIC | curses.color_pair(1))
    pad.attroff(curses.color_pair(1))

    # Display each menu option
    for i, option in enumerate(menu_options):
        x = box_start_x + ((2 * w // 3) - len(option)) // 2  # Centered horizontally
        y = start_y + i + 2

        if i == selected_row:
            pad.addstr(y, x, option, curses.A_REVERSE)
        else:
            pad.addstr(y, x, option)


def display_menu_box4(pad, start_y, w, menu_options, header, curses, selected_row):
    box_start_x = (w - (2 * w // 3)) // 2  # Centered horizontally
    box_end_x = 2 * w // 3

    # Draw box
    pad.attron(curses.color_pair(1))
    pad.hline(start_y, box_start_x, curses.ACS_HLINE, box_end_x)
    pad.hline(start_y + len(menu_options) + 3, box_start_x, curses.ACS_HLINE, box_end_x)
    pad.vline(start_y + 1, box_start_x, curses.ACS_VLINE, len(menu_options) + 2)
    pad.vline(start_y + 1, box_start_x + box_end_x - 1, curses.ACS_VLINE, len(menu_options) + 2)

    pad.addch(start_y, box_start_x, curses.ACS_ULCORNER)
    pad.addch(start_y + len(menu_options) + 3, box_start_x, curses.ACS_LLCORNER)
    pad.addch(start_y, box_start_x + box_end_x - 1, curses.ACS_URCORNER)
    pad.addch(start_y + len(menu_options) + 3, box_start_x + box_end_x - 1, curses.ACS_LRCORNER)

    # Display header
    header_x = box_start_x + 2
    pad.addstr(start_y, header_x, header, curses.A_ITALIC | curses.color_pair(1))
    pad.attroff(curses.color_pair(1))

    # Display each menu option
    for i, option in enumerate(menu_options):
        x = box_start_x + ((2 * w // 3) - len(option)) // 2  # Centered horizontally
        y = start_y + i + 2

        if i == selected_row:
            pad.addstr(y, x, option, curses.A_REVERSE)
        else:
            pad.addstr(y, x, option)


def update_selected_row(selected_row, key, group_start_index, group_end_index, curses):
    if key == curses.KEY_DOWN:
        if selected_row < group_end_index - group_start_index:
            selected_row += 1
        else:
            selected_row = 0  # Move to the first element of the next group
    elif key == curses.KEY_UP:
        if selected_row > 0:
            selected_row -= 1
        else:
            selected_row = group_end_index - group_start_index - 1  # Move to the last element of the previous group

    return selected_row


def main_menu_options(menu_options, box_start_x, box_start_y, w, selected_row, stdscr, curses):
    for i, option in enumerate(menu_options):
        x = box_start_x + ((2 * w // 3) - len(option)) // 2  # (Centered horizontally)
        y = box_start_y + i + 2

        if i == selected_row:
            stdscr.addstr(y, x, option, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option)


def groups_menu_options(menu_options, box_start_x, box_start_y, w, selected_row, stdscr, curses):
    for i, option in enumerate(menu_options):
        x = box_start_x + ((2 * w // 3) - len(option['name'])) // 2
        y = box_start_y + i + 2

        if i == selected_row:
            stdscr.addstr(y, x, option['name'], curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option['name'])
        y += 1


def host_group_options(menu_options, box_start_x, box_start_y, w, selected_row, stdscr, curses, isReadOnly, selected_hosts):
    for i, host in enumerate(menu_options):
        y = box_start_y + i + 2
        x = box_start_x + ((2 * w // 3) - len(host)) // 2

        if i == selected_row:
            if (isReadOnly == False):
                if i in selected_hosts:
                    stdscr.addstr(y, x, host, curses.color_pair(3) | curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, host, curses.color_pair(2) | curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, host, curses.A_REVERSE)
        elif i in selected_hosts:
            stdscr.addstr(y, x, host, curses.color_pair(3))
        else:
            if (isReadOnly == False):
                stdscr.addstr(y, x, host, curses.color_pair(2))
            else:
                stdscr.addstr(y, x, host)
        y += 1


def script_menu_options(menu_options, title_y, title, w, selected_row, stdscr, curses):
    script_x = [title_y + len(title) + 4 + i for i in range(len(menu_options))]
    for i in range(len(menu_options)):
        # Determine the attribute (A_NORMAL or A_REVERSE) based on whether the row is selected
        attr = curses.A_REVERSE if selected_row == script_x[i] else curses.A_NORMAL
        # Add the string to the screen with the appropriate attribute
        stdscr.addstr(script_x[i], w // 2 - len(menu_options[i]) // 2, menu_options[i], attr)


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
    modal_height = 11
    modal_text = ("Context information:"
                  "\n\nSPACE - scroll whole page down"
                  "\ny / Y - scroll whole page up\ng / G - scroll to next info tab"
                  "\nb / B - scroll to previous info tab\n\nq / Q - go back to host list"
                  "\nh / H - close context menu")
    # Calculate the position to draw the modal (top-right corner)
    modal_y = pad_pos + 1
    modal_x = pad.getmaxyx()[1] - modal_width - 1

    for y in range(modal_y, modal_y + modal_height):
        pad.addstr(y, modal_x, ' ' * modal_width)

    # Create a window for the modal
    modal_win = pad.subpad(modal_height, modal_width, modal_y, modal_x)

    # Clear the area behind the modal

    # Draw the box for the modal
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    modal_win.attron(curses.color_pair(2))
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
            modal_win.addstr(i + 1, 1, prefix, curses.A_BOLD | curses.color_pair(2))
            # Add the remaining part of the line without bold attribute
            modal_win.addstr(suffix)
    modal_win.attroff(curses.color_pair(2))


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


def script_menu_modal(stdscr, family, height, width, hosts, ports, usernames, doc_ports, doc_locations, doc_manifests,
                      doc_chkrootkit, doc_audit, curses):
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
                    functions.get_port_info(hosts, ports, usernames, *doc_ports)
                else:
                    portsss = port_input.split()
                    functions.get_port_info(hosts, ports, usernames, *portsss)
                modal.addstr(7, 2, f"Ports file created in tengui/ ", curses.A_BOLD)
                modal.addstr(10, 2, 'Press q to go back')
                modal.refresh()
            elif key == ord('q'):
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                port_input = port_input[:-1]
            elif is_numeric_char(key):
                port_input += chr(key)

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
                    functions.run_backup_script(hosts, ports, usernames, *doc_locations)
                else:
                    folders = directory_input.split()
                    functions.run_backup_script(hosts, ports, usernames, *folders)
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
                functions.run_lynis(usernames, hosts, ports)
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
                    functions.run_manifest_script(hosts, ports, usernames, *flattened_list)
                else:
                    folders = directory_input.split()
                    functions.run_manifest_script(hosts, ports, usernames, *folders)
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
                    functions.run_chkrootkit_script(hosts, ports, usernames, *doc_chkrootkit)
                else:
                    folders = directory_input.split()
                    functions.run_chkrootkit_script(hosts, ports, usernames, *folders)
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
                    functions.run_audit_setup_script(hosts, ports, usernames, *doc_audit)
                else:
                    folders = directory_input.split()
                    functions.run_audit_setup_script(hosts, ports, usernames, *folders)
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
                    functions.run_audit_retrieve_script(hosts, ports, usernames, *doc_audit)
                else:
                    folders = directory_input.split()
                    functions.run_audit_retrieve_script(hosts, ports, usernames, *folders)
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
                    functions.run_custom_command_script(hosts, ports, usernames, *doc_audit)
                else:
                    functions.run_custom_command_script(hosts, ports, usernames, directory_input)
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


