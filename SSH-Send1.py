import paramiko
import time
import sys
import os.path
import re
from getpass import getpass

# Ask for username and password at the start of script to be used for SSH connection to devices.
username = input("Please enter your username for SSH: ")
password = getpass("Please enter your password for SSH: ")


# Ask and verify the file containing host list, hostnames should be one per line.
path = os.path.dirname(os.path.abspath(__file__))
hostfile = path+"/queryhosts.list"

if os.path.isfile(hostfile):
    print("\nBelow hosts will be accessed: \n")
    hosts1 = open(hostfile, "r")
    hosts1text = hosts1.read()
    print(hosts1text)
    hosts1.seek(0)

    # User input to verify hosts are correct
    proceed_hosts = input("\n Please enter 'Yes' to continue or 'No' to exit: \n")

    if proceed_hosts == "Yes":
        hosts_list = hosts1.readlines()

    elif proceed_hosts == "No":
        sys.exit()

    else:
        sys.exit()

    hosts1.close()

else:
    print("\n* File {} does not exist :( Please check and try again.\n".format(hostfile))
    sys.exit()

# Ask and verify the file containing commands to run on the listed hosts, commands should be one per line.
path = os.path.dirname(os.path.abspath(__file__))
hostcommands = path+"/querycommands.list"

if os.path.isfile(hostcommands):
    print("\nBelow commands will be run: \n")
    commands1 = open(hostcommands, "r")
    commands1text = commands1.read()
    print(commands1text)
    commands1.seek(0)

    # User input to verify hosts are correct
    proceed_commands = input("\n Please enter 'Yes' to continue or 'No' to exit: \n")

    if proceed_commands == "Yes":
        commands_list = commands1.readlines()

    elif proceed_commands == "No":
        sys.exit()

    else:
        sys.exit()

    commands1.close()

else:
    print("\n* File {} does not exist :( Please check and try again.\n".format(hostcommands))
    sys.exit()

# port = input("Enter port number for SSH connection")
port = 22

# iterate hosts list
for host in hosts_list:
    host = host.strip()

    # Creating SSH CONNECTION
    try:
        # Logging into device
        session = paramiko.SSHClient()

        # This allows auto-accepting unknown host keys
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the device using username and password
        session.connect(host, port, username=username, password=password, timeout=None)
        print(f"SSH connection established to ... {host} \n")

        # Start an interactive shell session on the router
        connection = session.invoke_shell()
        # Clear the buffer on the screen
        output = connection.recv(1000)
        time.sleep(2)

        # Setting terminal length for entire output - disable pagination
        connection.send(b"\nterminal length 0\n")
        time.sleep(2)

        # Iterate commands to run
        for command in commands_list:
            command = command.strip()
            connection.send(command.encode('ascii'))
            time.sleep(3)
            connection.send(b"\n")
            time.sleep(2)

            # Receive buffer output
            file_output = connection.recv(8000).decode('ascii')
            time.sleep(2)

            if re.search("% Invalid input", file_output):
                print("There was at least one syntax error on device")

            # Print the output interactively to the CLI
            print(str(file_output))
            time.sleep(2)

        # Closing the connection
        session.close()
        print(f"\nClosed SSH to ... {host}\n")

    except paramiko.AuthenticationException:
        print("* Invalid username or password \n* Please check the username/password file or the device configuration.")
        print("* Closing program... Bye!")
        break
