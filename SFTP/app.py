import pysftp
import time
import os
import random
import string
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import datetime

# Set up connection parameters
hostname = ''
username = ''
password = ''
remote_dir = '/'
local_dir_received = '/temp/Order confirmation received'
local_dir_sent = '/temp/Order confirmation sent'

# Connect to SFTP server


def CheckAndDownload():
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(hostname, username=username, password=password, cnopts=cnopts) as sftp:
        print("Connected to SFTP server")
        # Change to remote directory
        sftp.chdir(remote_dir)
        print(f"Changed to directory {remote_dir}")
        # Monitor for new files
        while True:
            # Get list of files in remote directory
            remote_files = sftp.listdir()
            # Check for new files
            for file_name in remote_files:
                if file_name in ('.', '..'):
                    continue

                if sftp.isdir(file_name):
                    print(f"Skipping directory {file_name}")
                    continue

                local_path = f"{local_dir_received}/{file_name}"
                if os.path.exists(local_path):
                    print(
                        f"Skipping file {file_name} (already downloaded a file with the same name)")
                    continue

                # Download file
                sftp.get(file_name, localpath=local_path)
                print(f"Downloaded file {file_name} to {local_path}")
                # Delete file from remote directory
                sftp.remove(file_name)
                print(f"Deleted file {file_name} from remote directory")
            # Wait for 10 seconds before checking for new files again
            time.sleep(10)


def checkAndUpload():
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(hostname, username=username, password=password, cnopts=cnopts) as sftp:
        print("Connected to SFTP server")

        # Change to remote directory
        sftp.chdir(remote_dir)
        print(f"Changed to directory {remote_dir}")

        # Monitor for new files
        #while True:
            # Get list of files in local directory
        local_files = os.listdir(local_dir_sent)

        # Check for new files
        for file_name in local_files:
            if file_name in ('.', '..'):
                continue

            local_path = f"{local_dir_sent}/{file_name}"
            if sftp.exists(file_name):
                print(f"Skipping file {file_name} (already uploaded)")
                continue

            # Upload file
            sftp.put(local_path, remotepath=file_name)
            print(f"Uploaded file {file_name} to remote directory")

            # Delete file from local directory
            os.remove(local_path)
            print(f"Deleted file {file_name} from local directory")

            # Wait for 10 seconds before checking for new files again
            #time.sleep(10)


# Define function to generate random order confirmation XML
def generate_order_confirmation(order_number):
    # Generate random customer name
    first_name = ''.join(random.choices(string.ascii_uppercase, k=3))
    last_name = ''.join(random.choices(string.ascii_uppercase, k=5))
    customer_name = f"{first_name} {last_name}"

    # Generate random order total
    total_price = round(random.uniform(10, 1000), 2)

    # Generate random shipping address
    address_line_1 = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=8)) + " St."
    address_line_2 = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=6)) + " Ave."
    city = ''.join(random.choices(string.ascii_uppercase, k=8))
    state = ''.join(random.choices(string.ascii_uppercase, k=2))
    zip_code = ''.join(random.choices(string.digits, k=5))
    country = "USA"

    # Create XML tree
    root = ET.Element("orderConfirmation")
    ET.SubElement(root, "orderNumber").text = str(order_number)
    ET.SubElement(root, "customerName").text = customer_name
    ET.SubElement(root, "orderDate").text = datetime.datetime.now().strftime(
        '%Y-%m-%d')
    ET.SubElement(root, "totalPrice").text = str(total_price)
    shipping_address = ET.SubElement(root, "shippingAddress")
    ET.SubElement(shipping_address, "addressLine1").text = address_line_1
    ET.SubElement(shipping_address, "addressLine2").text = address_line_2
    ET.SubElement(shipping_address, "city").text = city
    ET.SubElement(shipping_address, "state").text = state
    ET.SubElement(shipping_address, "zipCode").text = zip_code
    ET.SubElement(shipping_address, "country").text = country

    # Generate XML string and pretty-print it
    xml_string = ET.tostring(root, encoding="unicode")
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")

    # Return the pretty-formatted XML string
    return pretty_xml


def generateXML(x: int):
    # Generate x order confirmation XML files
    directory = r"C:\Users\Morten\Desktop\github\flask\SFTP_API\from_bestseller"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i in range(1, x+1):
        # Generate XML content
        xml_content = generate_order_confirmation(i)

        # Write XML to file
        file_name = os.path.join(directory, f"orderConfirmation_{i}.xml")
        with open(file_name, "w") as f:
            f.write(xml_content)

        # Print status message
        if i % 500 == 0:
            print(f"Generated {i} XML files") 


#dir = "C:\Users\Morten\Desktop\github\flask\SFTP_API\downloadfile\"
generateXML(8000)
'''
'''
start_time = time.time()
#checkAndUpload()
# CheckAndDownload()
end_time = time.time()

elapsed_time = end_time - start_time
print(f"My function took {elapsed_time} seconds to complete.")