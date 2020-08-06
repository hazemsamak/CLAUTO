import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from texttable import Texttable as TT
from getpass import getpass
import xmltodict
import re
from axl import mac_set

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

if __name__ == "__main__":

    # Disable certificate warnings
    disable_warnings(InsecureRequestWarning)

    print()
    cucm_ip = "10.1.5.5"
    cucm_user = "Administrator"
    cucm_pw = "C0ll@B"
    ip = "10.1.5.155"
    user = "admin"
    pw = ""
    old_mac = "000000000000"
    new_mac = input("Enter MAC Address: ")
    if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", new_mac.lower()):
        print("Not A Valid MAC Address")

    else:
        server = "https://{}/".format(ip)
        print()

        # Reset system name
        xml = '''<?xml version="1.0"?>
                <Configuration>
                    <SystemUnit>
                        <Name/>
                    </SystemUnit>
                </Configuration>'''
        reply = post_call(xml)
        if "error" in reply:
                print(reply["error"])
        else:
            result = reply["success"]["Configuration"]
            if "Success" in result:
                print("System Name Reset")
            else:
                print("Unknown Error")

        # Reset custom message
        xml = '''<?xml version="1.0"?>
                <Configuration>
                    <UserInterface>
                        <CustomMessage/>
                    </UserInterface>
                </Configuration>'''
        reply = post_call(xml)
        if "error" in reply:
                print(reply["error"])
        else:
            result = reply["success"]["Configuration"]
            if "Success" in result:
                print("Custom Message Reset")
            else:
                print("Unknown Error")

        # Remove all panels
        xml = '''<?xml version="1.0"?>
                <Command>
                    <UserInterface>
                        <Extensions>
                            <Clear/>
                        </Extensions>
                    </UserInterface>
                </Command>'''
        reply = post_call(xml)
        if "error" in reply:
                print(reply["error"])
        else:
            result = reply["success"]["Command"]["ExtensionsClearResult"]
            if result["@status"] == "OK":
                print("Custom Panels Cleared")
            else:
                print("Unknown Error")

        # Remove macro
        xml = '''<?xml version="1.0"?>
                <Command>
                    <Macros>
                        <Macro>
                            <Remove>
                                <Name>macro</Name>
                            </Remove>
                        </Macro>
                    </Macros>
                </Command>'''
        reply = post_call(xml)
        if "error" in reply:
                print(reply["error"])
        else:
            result = reply["success"]["Command"]["MacroRemoveResult"]
            if result["@status"] == "OK":
                print("Macro Removed")
            elif result["@status"] == "Error":
                if result["Reason"] == "No such macro: macro":
                    print("Macro Removed")
            else:
                print("Unknown Error")

        # Set CUCM mode
        xml = '''<?xml version="1.0"?>
                <Configuration>
                    <Provisioning>
                        <Connectivity>Auto</Connectivity>
                        <ExternalManager>
                            <Address>10.1.5.5</Address>
                            <AlternateAddress></AlternateAddress>
                            <Domain></Domain>
                            <Path></Path>
                            <Protocol>HTTPS</Protocol>
                        </ExternalManager>
                        <LoginName></LoginName>
                        <Mode>CUCM</Mode>
                    </Provisioning>
                </Configuration>'''
        reply = post_call(xml)
        if "error" in reply:
                print(reply["error"])
        else:
            result = reply["success"]["Configuration"]
            if "Success" in result:
                print("CUCM Mode Set")
            else:
                print("Unknown Error")

        # Update MAC in CUCM
        print(mac_set(cucm_ip, cucm_user, cucm_pw, old_mac, new_mac))
        print()
        