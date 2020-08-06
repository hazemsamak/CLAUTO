import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from texttable import Texttable as TT
from getpass import getpass
import xmltodict

# Function to print data in table
def table(header, data):
    # Sort all data alphabetically by first column
    data.sort(key=lambda pattern: pattern[0])
    report = header + data
    table = TT(max_width=0)
    # Set all columns to type "text"
    dtype = []
    for count in range(0, len(header[0])):
        dtype.append('t')
    table.set_cols_dtype(dtype)
    table.add_rows(report)
    return table.draw()

# Function to POST information to video endpoint
def post_call(xml):
    url = server + "putxml"
    try:
        reply = requests.post(url, auth=(user, pw), data=xml, verify=False)
    # User request error
    except requests.exceptions.RequestException as err:
        return {"error": err}
    # Return values based on request response
    else:
        if reply.status_code == 200:
            result = xmltodict.parse(reply.content)
            return {"success": result}
        elif reply.status_code == 401:
            return {"error": "Invalid Credentials"}
        else:
            return {"error": "Unknown Result"}

# Function to GET information from video endpoint
def get_call(path):
    url = server + "getxml/?location=/" + path
    try:
        reply = requests.get(url, auth=(user, pw), verify=False)
    # User request error
    except requests.exceptions.RequestException as err:
        return {"error": err}
    # Return values based on request response
    else:
        if reply.status_code == 200:
            result = xmltodict.parse(reply.content)
            return {"success": result}
        elif reply.status_code == 401:
            return {"error": "Invalid Credentials"}
        else:
            return {"error": "Unknown Result"}

if __name__ == "__main__":

    # Disable certificate warnings
    disable_warnings(InsecureRequestWarning)

    print()
    ip = input("Enter Room IP: ")
    user = input("Enter Room ID: ")
    pw = getpass("Enter Rooom Password: ")

    server = "https://{}/".format(ip)

    while True:
        # Menu
        print()
        print("1. Place Call")
        print("2. List Active Calls")
        print("3. Place Call On Hold")
        print("4. Take Call Off Hold")
        print("5. End Call")
        print("9. Quit")
        print()
        option = input("Enter Option: ")

        # Place a call
        if option == "1":
            print()
            number = input("Phone Number: ")
            print()
            # Set XML body for placing call
            xml = '''<?xml version="1.0"?>
                    <Command>
                        <Dial>
                            <Number>{}</Number>
                        </Dial>
                    </Command>'''.format(number)
            reply = post_call(xml)
            if "error" in reply:
                    print(reply["error"])
            else:
                header = [["Number", "Call ID", "Conference ID"]]
                dial_info = reply["success"]["Command"]["DialResult"]
                data = [[number, dial_info["CallId"], dial_info["ConferenceId"]]]
                print(table(header, data))

        # List all calls
        if option == "2":
            print()
            path = "Status/Call"
            reply = get_call(path)
            if "error" in reply:
                print(reply["error"])
            # Check if no active calls
            elif "EmptyResult" in reply["success"]:
                    print("No Active Calls")
            else:
                header = [["Call ID", "Remote Number", "Display Name", "Status", "Call Type", "Direction", "Duration (sec)",
                            "TX Rate", "RX Rate"]]
                data = []
                call = reply["success"]["Status"]["Call"]
                # If type "list", then more than one call
                if isinstance(call, list):
                    # Iterate over all calls and pull call data from appropriate keys
                    for item in reply["success"]["Status"]["Call"]:
                        data.append([item["@item"], item["RemoteNumber"], item["DisplayName"], item["Status"], item["CallType"], 
                                    item["Direction"], item["Duration"], item["TransmitCallRate"], item["ReceiveCallRate"]])
                else:
                    # Pull call data from appropriate keys for single call
                    data.append([call["@item"], call["RemoteNumber"], call["DisplayName"], call["Status"], call["CallType"], 
                                call["Direction"], call["Duration"], call["TransmitCallRate"], call["ReceiveCallRate"]])
                print(table(header, data))

        # Place a call on hold
        if option == "3":
            print()
            call_id = input("Call ID: ")
            print()
            # Set XML body for placing call on hold
            xml = '''<?xml version="1.0"?>
                    <Command>
                        <Call>
                            <Hold>
                                <CallId>{}</CallId>
                            </Hold>
                        </Call>
                    </Command>'''.format(call_id)
            reply = post_call(xml)
            if "error" in reply:
                    print(reply["error"])
            else:
                result = reply["success"]["Command"]["CallHoldResult"]
                if result["@status"] == "OK":
                    print("Call {} Placed On Hold".format(call_id))
                elif result["Cause"] == "12":
                    print("Call ID Not Found")
                elif result["Cause"] == "16":
                    print("Call Already On Hold")
                else:
                    print("Unknown Error")

        # Take a call off hold
        if option == "4":
            print()
            call_id = input("Call ID: ")
            print()
            # Set XML body for taking call off hold
            xml = '''<?xml version="1.0"?>
                    <Command>
                        <Call>
                            <Resume>
                                <CallId>{}</CallId>
                            </Resume>
                        </Call>
                    </Command>'''.format(call_id)
            reply = post_call(xml)
            if "error" in reply:
                    print(reply["error"])
            else:
                result = reply["success"]["Command"]["CallResumeResult"]
                if result["@status"] == "OK":
                    print("Call {} Taken Off Hold".format(call_id))
                elif result["Cause"] == "12":
                    print("Call ID Not Found")
                else:
                    print("Unknown Error")

        # Disconnect a call
        if option == "5":
            print()
            call_id = input("Call ID: ")
            print()
            # Set XML body for disconnecting a call
            xml = '''<?xml version="1.0"?>
                    <Command>
                        <Call>
                            <Disconnect>
                                <CallId>{}</CallId>
                            </Disconnect>
                        </Call>
                    </Command>'''.format(call_id)
            reply = post_call(xml)
            if "error" in reply:
                    print(reply["error"])
            else:
                result = reply["success"]["Command"]["CallDisconnectResult"]
                if result["@status"] == "OK":
                    print("Call {} Disconnected".format(call_id))
                else:
                    print("Unknown Error")

        # Option to quit
        if option == "9":
            print()
            break