import pysftp
import time
import threading
import csv
import datetime
import test

# Set the hostname, username, and password for the SFTP server
HOSTNAME = ''
#USERNAME = ''
#PASSWORD = ''


# Set the interval in minutes between checks
CHECK_INTERVAL = 1

# Connect to the SFTP server
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None


def check_sftp():

    USERNAME = ''
    PASSWORD = ''
    while True:
        try:
            with pysftp.Connection(host=HOSTNAME, username=USERNAME, password=PASSWORD, cnopts=cnopts) as sftp:
                # Change to the desired subfolder
                sftp.chdir("/")

                # Disconnect from the SFTP server
                sftp.close()

        except Exception as e:
            print(f'Error: {e}')

        # Sleep for the specified interval
        time.sleep(CHECK_INTERVAL * 1)

# Create and start the threads
num_threads = 20
threads = []
my_file = open(r"")
# reading the file
data = my_file.read()
# replacing end of line('/n') with ' ' and
# splitting the text it further when '.' is seen.
data_into_list = data.replace('\n', ' ').split(".")
# printing the data
print(data_into_list)
my_file.close()
for i in range(num_threads):
    t = threading.Thread(target=check_sftp)
    threads.append(t)
    t.start()