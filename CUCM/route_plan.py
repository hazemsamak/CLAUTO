from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from getpass import getpass
from axl import server_check, route_print

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
                # Call function to print route plan
                print(route_print(server, acct, pw))