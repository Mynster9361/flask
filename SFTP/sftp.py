import pysftp
import time
import threading
import csv
import datetime

# Set the hostname, username, and password for the SFTP server
HOSTNAME = ''
USERNAME = ''
PASSWORD = ''

# Set the path to the subfolder on the SFTP server
SUBFOLDER_PATH = '/'

# Set the interval in minutes between checks
CHECK_INTERVAL = 1

# Connect to the SFTP server
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
old_files = []

# Define the callbacks
def fcallback(entry):
    if entry not in old_files:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        with open('errors.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp, ':New file:', {entry}])
        print(f'New file: {entry}')
        old_files.append(entry)

def dcallback(entry):
    pass

def ucallback(entry):
    pass
global entry
def check_sftp():
    while True:
        try:
            with pysftp.Connection(host=HOSTNAME, username=USERNAME, password=PASSWORD, cnopts=cnopts) as sftp:
                # Change to the desired subfolder
                sftp.chdir(SUBFOLDER_PATH)

                # Recursively list all files in the specified subfolder and its subfolders
                entries = sftp.walktree(SUBFOLDER_PATH, fcallback=fcallback, dcallback=dcallback, ucallback=ucallback)
                
                if entries:
                    print([entry.filename for entry in entries])
                    old_files = [entry.filename for entry in entries]
                    
                # Disconnect from the SFTP server
                sftp.close()

        except Exception as e:
            with open('errors.csv', 'a', newline='') as csvfile:
                now = datetime.datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, ':Error:', {e}])
            print(f'Error: {e}')

        # Sleep for the specified interval
        time.sleep(CHECK_INTERVAL * 1)

# Create and start the threads
num_threads = 230
threads = []
for i in range(num_threads):
    t = threading.Thread(target=check_sftp)
    threads.append(t)
    t.start()