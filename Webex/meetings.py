import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from texttable import Texttable as TT
from getpass import getpass
import xmltodict

# Function to call Webex API
def api_call(xml):
    try:
        reply = requests.post("https://api.webex.com/WBXService/XMLService", data=xml, verify=False, headers={"Content-Type": "application/xml"})
    except requests.exceptions.RequestException as err:
        return {"error": err}
    else:
        # Check if successful API call
        if reply.status_code == 200:
            # Convert XML response to dict; Pull <message><header><response><result> value
            result = xmltodict.parse(reply.content)["serv:message"]["serv:header"]["serv:response"]["serv:result"]
            # Pull <message><body><bodyContent> and return with success
            body = xmltodict.parse(reply.content)["serv:message"]["serv:body"]["serv:bodyContent"]
            if result == "SUCCESS":
                return {"success": body}
            else:
                # Pull <message><header><response><reason> and return with error
                reason = xmltodict.parse(reply.content)["serv:message"]["serv:header"]["serv:response"]["serv:reason"]
                return {"error": reason} 
        elif reply.status_code == 404:
            return {"error": "Invalid Site Name"}
        else:
            return {"error": reply.content}

# Function to print data in table
def table(header, data):
    # Sort all data alphabetically by fourth column
    data.sort(key=lambda pattern: pattern[3])
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

    while True:
        print()
        site = input("Enter Webex Site Name: ")
        user = input("Enter Webex ID: ")
        pw = getpass("Enter Webex Password: ")
        # Set XML body for "AuthenticateUser" call
        xml = '''<message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <header>
                        <securityContext>
                        <siteName>{site}</siteName>
                        <webExID>{user}</webExID>
                        <password>{pw}</password>
                        </securityContext>
                    </header>
                    <body>
                        <bodyContent xsi:type="java:com.webex.service.binding.user.AuthenticateUser">
                        </bodyContent>
                    </body>
                    </message>'''.format(site=site, user=user, pw=pw)
        response = api_call(xml)
        if "error" in response:
            print(response["error"])
        else:
            # Capture session ticket for authenticating API calls
            ticket = response["success"]["use:sessionTicket"]
            break

    while True:
        # Menu
        print()
        print("1. List Meetings")
        print("2. Create Meeting")
        print("3. Delete Meeting")
        print("9. Quit")
        print()
        option = input("Enter Option: ")

        # List all meetings
        if option == "1":
            print()
            # Set XML body for "LstsummaryMeeting" call
            xml = '''<message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                        <header>
                            <securityContext>
                            <siteName>{site}</siteName>
                            <webExID>{user}</webExID>
                            <sessionTicket>{ticket}</sessionTicket>
                            </securityContext>
                        </header>
                        <body>
                            <bodyContent xsi:type="java:com.webex.service.binding.meeting.LstsummaryMeeting">
                            </bodyContent>
                        </body>
                        </message>'''.format(site=site, user=user, ticket=ticket)
            response = api_call(xml)
            if "error" in response:
                print(response["error"])
            else:
                header = [["Meeting Key", "Conference Name", "Host ID", "Start Date/Time", "Time Zone", "Duration", "Status"]]
                data = []
                meeting = response["success"]["meet:meeting"]
                # If type "list", then more than one meeting
                if isinstance(meeting, list):
                    # Iterate over all meetings and pull meeting data from appropriate keys
                    for item in meeting:
                        data.append([item["meet:meetingKey"], item["meet:confName"], item["meet:hostWebExID"], item["meet:startDate"],
                                    item["meet:timeZone"], item["meet:duration"], item["meet:status"]])
                else:
                    # Pull meeting data from appropriate keys for single meeting
                    data.append([meeting["meet:meetingKey"], meeting["meet:confName"], meeting["meet:hostWebExID"], meeting["meet:startDate"],
                                meeting["meet:timeZone"], meeting["meet:duration"], meeting["meet:status"]])
                print(table(header, data))

        # Create a new meeting
        if option == "2":
            print()
            conf_name = input("Enter Conference Name: ")
            passcode = input("Enter Meeting Passcode: ")
            date = input("Enter Start Date (MM/DD/YYYY): ")
            time = input("Enter Start Time (HH:MM:SS): ")
            duration = input("Enter Duration in Minutes: ")
            print()
            # Set XML body for "CreateMeeting" call
            xml = '''<message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                        <header>
                            <securityContext>
                            <siteName>{site}</siteName>
                            <webExID>{user}</webExID>
                            <sessionTicket>{ticket}</sessionTicket>
                            </securityContext>
                        </header>
                            <body>
                                <bodyContent
                                    xsi:type="java:com.webex.service.binding.meeting.CreateMeeting">
                                    <accessControl>
                                        <meetingPassword>{passcode}</meetingPassword>
                                    </accessControl>
                                    <metaData>
                                        <confName>{conf_name}</confName>
                                    </metaData>
                                    <enableOptions>
                                        <chat>true</chat>
                                        <audioVideo>true</audioVideo>
                                        <autoRecord>true</autoRecord>
                                    </enableOptions>
                                    <schedule>
                                        <startDate>{date} {time}</startDate>
                                        <duration>{duration}</duration>
                                    </schedule>
                                </bodyContent>
                            </body>
                        </message>'''.format(site=site, user=user, ticket=ticket, passcode=passcode, conf_name=conf_name, 
                                            date=date, time=time, duration=duration)
            response = api_call(xml)
            if "error" in response:
                print(response["error"])
            else:
                header = [["Passcode", "Conference Name", "Host ID", "Start Date/Time", "Duration"]]
                data = [[passcode, conf_name, user, "{} {}".format(date, time), duration]]
                print(table(header, data))

        # Delete a meeting
        if option == "3":
            print()
            key = input("Enter Meeting Key: ")
            print()
            # Set XML body for "DelMeeting" call
            xml = '''<message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                        <header>
                            <securityContext>
                            <siteName>{site}</siteName>
                            <webExID>{user}</webExID>
                            <sessionTicket>{ticket}</sessionTicket>
                            </securityContext>
                        </header>
                            <body>
                                <bodyContent
                                    xsi:type="java:com.webex.service.binding.meeting.DelMeeting">
                                    <meetingKey>{key}</meetingKey>
                                </bodyContent>
                            </body>
                        </message>'''.format(site=site, user=user, ticket=ticket, key=key)
            response = api_call(xml)
            if "error" in response:
                print(response["error"])
            else:
                print("Meeting With Key {} Has Been Deleted".format(key))

        # Option to quit
        if option == "9":
            print()
            break
