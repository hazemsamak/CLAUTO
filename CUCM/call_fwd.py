from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from getpass import getpass
from axl import server_check, cfa_check, cfa_set

if __name__ == "__main__":

    # Disable certificate warnings
    disable_warnings(InsecureRequestWarning)

    while True:
        # Input CUCM IP address
        server = input("CUCM IP Address (Q to quit): ")
        # Allow option to quit
        if server == "Q" or server == "q":
            break
        else:
            # Validate server is reachable
            if not server_check(server):
                print("{} Unreachable".format(server))
            else:
                # Collect server credentials
                acct = input("CUCM ID: ")
                pw = getpass("CUCM PW: ")
                dn = input("Directory Number to Set Call Forward On: ")
                pt = input("Partition of Directory Number: ")
                # Call function to check call forward setting
                print(cfa_check(server, acct, pw, dn, pt))
                dest = input("Destination Number to Set Call Forward To: ")
                css = input("Calling Search Space for Call Forward: ")
                # Call function to check call forward setting
                print(cfa_set(server, acct, pw, dn, pt, dest, css))
                print(cfa_check(server, acct, pw, dn, pt))