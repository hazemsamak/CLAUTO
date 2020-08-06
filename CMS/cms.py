import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from texttable import Texttable as TT
from getpass import getpass
import xmltodict

# Function to print data in table
def table(header, data):
    # Sort all data alphabetically by second column
    data.sort(key=lambda pattern: pattern[1])
    report = header + data
    table = TT(max_width=0)
    # Set all columns to type "text"
    dtype = []
    for count in range(0, len(header[0])):
        dtype.append('t')
    table.set_cols_dtype(dtype)
    table.add_rows(report)
    return table.draw()

if __name__ == "__main__":

    # Disable certificate warnings
    disable_warnings(InsecureRequestWarning)

    # Set CMS server URL
    url = "https://10.1.5.23:445"

    print()
    user = input("Enter CMS ID: ")
    pw = getpass("Enter CMS Password: ")

    while True:
        # Menu
        print()
        print("1. List CMS Spaces")
        print("2. Create CMS Space")
        print("3. Delete CMS Space")
        print("9. Quit")
        print()
        option = input("Enter Option: ")

        # List all spaces
        if option == "1":
            print()
            # Set path for "coSpaces" call
            path = "/api/v1/coSpaces"
            try:
                # GET call to obtain list of spaces
                reply = requests.get(url + path, auth=(user, pw), verify=False)
            except requests.exceptions.RequestException as err:
                print(err)
            else:
                if reply.status_code == 200:
                    response = xmltodict.parse(reply.content)["coSpaces"]
                    header = [["Space ID", "Space Name", "URI Prefix", "Secondary URI Prefix", "Call ID"]]
                    data = []
                    space = response["coSpace"]
                    ref = ["@id", "name", "uri", "secondaryUri", "callId"]
                    # If type "list", then more than one space
                    if isinstance(space, list):
                        # Iterate over all spaces and pull meeting data from appropriate keys
                        for line in space:
                            values = []
                            # Iterate over each potential variable since not all variables are required
                            for item in ref:
                                if line.get(item):
                                    values.append(line.get(item))
                                else:
                                    values.append("")
                            data.append(values)                                
                    else:
                        # Pull meeting data from appropriate keys for single space
                        values = []
                        # Iterate over each potential variable since not all variables are required
                        for item in ref:
                            if space.get(item):
                                values.append(space.get(item))
                            else:
                                values.append("")
                        data.append(values) 
                    print(table(header, data))
                elif reply.status_code == 400:
                    # Failure descriptions are presented as XML tag
                    response = xmltodict.parse(reply.content)["failureDetails"]
                    print(next(iter(response)))
                elif reply.status_code == 401:
                    print("Invalid Credentials")
                else:
                    print("Status Code {}".format(reply.status_code))
                    print(reply.content)
                
        # Create a new space
        if option == "2":
            print()
            space_name = input("Enter Space Name: ")
            space_uri = input("Enter Space URI Prefix: ")
            passcode = input("Enter Space Passcode: ")
            print()
            # Set path for "coSpaces" call
            path = "/api/v1/coSpaces"
            vars = {"name": space_name, "uri": space_uri, "passcode": passcode}
            try:
                # POST call to create a new space
                reply = requests.post(url + path, auth=(user, pw), data=vars, verify=False)
            except requests.exceptions.RequestException as err:
                print(err)
            else:
                if reply.status_code == 200:
                    header = [["Space Name", "URI Prefix", "Passcode"]]
                    data = [[space_name, space_uri, passcode]]
                    print(table(header, data))
                elif reply.status_code == 400:
                    # Failure descriptions are presented as XML tag
                    response = xmltodict.parse(reply.content)["failureDetails"]
                    print(next(iter(response)))
                elif reply.status_code == 401:
                    print("Invalid Credentials")
                else:
                    print("Status Code {}".format(reply.status_code))
                    print(reply.content)

        # Delete a space
        if option == "3":
            print()
            space_id = input("Enter Space ID: ")
            print()
            # Set path for "coSpaces" call and add space ID
            path = "/api/v1/coSpaces/{}".format(space_id)
            try:
                # DELETE call to remove a space based on passed ID
                reply = requests.delete(url + path, auth=(user, pw), verify=False)
            except requests.exceptions.RequestException as err:
                print(err)
            else:
                if reply.status_code == 200:
                    print("Space With ID {} Has Been Deleted".format(space_id))
                elif reply.status_code == 400:
                    # Failure descriptions are presented as XML tag
                    response = xmltodict.parse(reply.content)["failureDetails"]
                    print(next(iter(response)))
                elif reply.status_code == 401:
                    print("Invalid Credentials")
                else:
                    print("Status Code {}".format(reply.status_code))
                    print(reply.content)

        # Option to quit
        if option == "9":
            print()
            break
