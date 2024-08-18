import os
import json
import datetime
import os.path
import time

interV = 15  # Script repeat interval in seconds
looper = False  # variable for deciding looping mechanisam
print(f"MR HEMANT Welcome to SMS forwarder v:1.1 by")
print('''
 ██████╗██╗     ██╗ ██████╗██╗  ██╗███████╗                           
██╔════╝██║     ██║██╔════╝██║ ██╔╝██╔════╝                           
██║     ██║     ██║██║     █████╔╝ ███████╗                           
██║     ██║     ██║██║     ██╔═██╗ ╚════██║                           
╚██████╗███████╗██║╚██████╗██║  ██╗███████║                           
 ╚═════╝╚══════╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝                           
             █████╗ ███╗   ██╗██████╗     ██████╗ ██╗████████╗███████╗
            ██╔══██╗████╗  ██║██╔══██╗    ██╔══██╗██║╚══██╔══╝██╔════╝
            ███████║██╔██╗ ██║██║  ██║    ██████╔╝██║   ██║   ███████╗
            ██╔══██║██║╚██╗██║██║  ██║    ██╔══██╗██║   ██║   ╚════██║
            ██║  ██║██║ ╚████║██████╔╝    ██████╔╝██║   ██║   ███████║
            ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝     ╚═════╝ ╚═╝   ╚═╝   ╚══════╝
''')
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# Defining function for forwarding sms
def smsforward(looping=False):
    global looper  # refferencing main looper varibale
    lastSMS = datetime.datetime.now()
    tmpFile = "tmpLastTime.txt"
    cfgFile = "config.txt"
    # Checking existance of configuration file
    if not os.path.exists(cfgFile):
        # file not found. creating a new configuration file
        cfile = open(cfgFile, "a")
        filters = input(f"{bcolors.BOLD}Please enter keyword filter(s) separated by comma (',') : {bcolors.ENDC}")
        filter_s = filters.split(",")
        cfile.write(filters.lower())
        cfile.write("\n")
        print("")
        print("")
        mnumbers = input(f"{bcolors.BOLD}Please enter mobile number(s) separated by comma (',') : {bcolors.ENDC}")
        mnumber_s = mnumbers.split(",")
        cfile.write(mnumbers)
        cfile.close()
    else:
            # configuration file is already there. reading configurations
        rst = "1"
        if not looping:
            print(f"""{bcolors.BOLD}Old configuration file found! What do You want to do?{bcolors.ENDC}
                {bcolors.OKGREEN}1) Continue with old settings{bcolors.ENDC}
                {bcolors.WARNING}2) Remove old settings and start afresh{bcolors.ENDC}""")
            rst = input("Please enter your choice number: ")
        if rst == "1":
            print(f"{bcolors.OKGREEN}Starting with old settings...........{bcolors.ENDC}")
            cfile = open(cfgFile, "r")
            cdata = cfile.read().splitlines()
            filter_s = cdata[0].split(",")
            mnumber_s = cdata[1].split(",")
        elif rst == "2":
            print(f"{bcolors.WARNING}Removing old Configuration files..........{bcolors.ENDC}")
            os.remove(cfgFile)
            os.remove(tmpFile)
            print(f"{bcolors.WARNING}Old configuration files removed. Please enter new settings{bcolors.ENDC}")
            smsforward()
    # Chcking last saved forward time
    if not os.path.exists(tmpFile):
        # Saved time time not found. Setting up and saving current time as last forwar dime
        print("Last time not found. Setting it to current Date-Time")
        tfile = open(tmpFile, "w")
        tfile.write(str(lastSMS))
        tfile.close()
    else:
        # Saved last sms forward time found. loading form that
        tfile = open(tmpFile, "r")
        lastSMS = datetime.datetime.fromisoformat(tfile.read())
        tfile.close()
    if not looper:
        # ask user to run the script on repeat
        lop = input(f"Keep running after each {interV} second (y/n): ")
        if lop == "y":
            looper = True  # This will keep the script after defined interval
            print("You can stop the script anytime by pressing Ctrl+C")
    print(f"Last SMS forwarded on {lastSMS}")
    

# Define your variables and settings
filter_s = ["keyword1", "keyword2"]  # List of keywords to filter SMS messages
mnumber_s = ["1234567890", "0987654321"]  # List of numbers to forward SMS to
tmpFile = "/path/to/tmpfile"  # Path to the temporary file where last SMS timestamp is stored

# Function to get the timestamp of the last processed SMS
def get_last_sms_timestamp():
    try:
        with open(tmpFile, "r") as tfile:
            last_sms_time = tfile.read().strip()
            return datetime.datetime.fromisoformat(last_sms_time)
    except (FileNotFoundError, ValueError):
        return datetime.datetime.min  # Return a very old date if file not found or date is invalid

# Function to update the timestamp of the last processed SMS
def update_last_sms_timestamp(timestamp):
    with open(tmpFile, "w") as tfile:
        tfile.write(timestamp.isoformat())

# Main function to read and process SMS
def process_sms():
    try:
        jdata = os.popen("termux-sms-list -l 50").read()  # Read the latest 50 SMSs
        jd = json.loads(jdata)  # Load JSON data
        print(f"Reading {len(jd)} latest SMSs")

        last_sms = get_last_sms_timestamp()

        for j in jd:
            received_time = datetime.datetime.fromisoformat(j['received'])
            if received_time > last_sms:  # Check if SMS is newer than the last processed SMS
                if j['type'] == "inbox":  # Ensure SMS is in the inbox
                    for f in filter_s:
                        if f in j['body'].lower():  # Check if SMS body matches any filter
                            print(f"{f} found")
                            for m in mnumber_s:
                                print(f"Forwarding to {m}")
                                os.system(f"termux-sms-send -n {m} {j['body']}")  # Forward SMS
                                update_last_sms_timestamp(received_time)  # Update last SMS timestamp

    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to process SMS
if __name__ == "__main__":
    process_sms()

smsforward()
# if user decided to repeat the script exexcution, the following loop will do that
while looper:
    time.sleep(interV)
    smsforward(looping=True)
