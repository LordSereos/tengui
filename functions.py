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

def get_elements_for_ip(ip_address, element):
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
