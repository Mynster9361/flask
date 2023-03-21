import requests
import json

# Set the number of records to retrieve per page
top = 200

# Initialize the list of vulnerabilities
vulnerabilities = []

# Loop through the pages of data
skip = 0
while True:
    if skip == 2000:
        break
    # Build the API URL with the $skip and $top parameters
    url = f"https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability?$skip={skip}&$top={top}"

    # Make the API request
    response = requests.get(url)
    print(response.status_code)
    # Check if there is any data returned
    if not response.content:
        break
    # Parse the JSON data
    data = json.loads(response.content)
    # Add the vulnerabilities to the list
    vulnerabilities.extend(data['value'])
    # Increment the skip counter
    skip += top

# Print the number of vulnerabilities retrieved
print(f"Retrieved {len(vulnerabilities)} vulnerabilities")
