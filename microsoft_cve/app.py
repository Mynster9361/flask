from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import json
import requests
import asyncio
import os
from datetime import datetime, timezone
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
from xml.etree.ElementTree import Element, SubElement, tostring
from feedgen.feed import FeedGenerator
fg = FeedGenerator()
# Initialize the FastAPI app and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

favicon_path = 'favicon.ico'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@app.get("/")
async def root(request: Request):
    # Call the update_vulnerabilities function to update the vulnerabilities data
    #update_vulnerabilities()
    # Open the 'vulnerabilities.json' file and load its data into the 'data' variable
    with open('vulnerabilities.json', 'r') as f:
        data = json.load(f)
    
    # Initialize an empty list to hold each vulnerability as a dictionary
    vulnerabilities = []
    
    # Define a list of keys to extract from each vulnerability object
    keys = ['cveNumber', 'cveTitle', 'releaseNumber', 'vulnType', 'latestRevisionDate',
            'mitreUrl', 'publiclyDisclosed', 'exploited', 'latestSoftwareRelease']
    
    # Loop through each vulnerability in the 'data' variable
    for vuln in data:
        # Initialize an empty dictionary to hold the vulnerability data
        vuln_dict = {}
        
        # Loop through each key in the 'keys' list and add its value to the 'vuln_dict' dictionary
        # If a key is not present in the vulnerability object, its value is set to 'N/A'
        for key in keys:
            vuln_dict[key] = vuln.get(key, 'N/A')
        # Add the 'baseScore' and 'temporalScore' values to the 'vuln_dict' dictionary
        vuln_dict['baseScore'] = vuln.get('baseScore', 'N/A')
        vuln_dict['temporalScore'] = vuln.get('temporalScore', 'N/A')
        # Add the 'vuln_dict' dictionary to the 'vulnerabilities' list
        vulnerabilities.append(vuln_dict)
    # Create a context dictionary containing the 'request' and 'vulnerabilities' variables
    context = {"request": request, "vulnerabilities": vulnerabilities}
    # Render the 'index.html' template with the 'context' dictionary and return the result
    return templates.TemplateResponse("index.html", context)


def get_latest():
    """
    This function returns the release date and latest revision date of the most recent vulnerability in 'vulnerabilities.json'
    in the format required by the Microsoft Security Update Guide API for filtering.
    """
    # Open the vulnerabilities.json file and load its contents as a dictionary
    with open('vulnerabilities.json', 'r') as f:
        data = json.load(f)
        
    # Initialize variables to None to track the latest release date and latest revision date
    release_date = None
    latest_revision_date = None

    # Iterate through each item in the data dictionary and update the release and revision dates if they are more recent
    for item in data:
        if not release_date or item['releaseDate'] > release_date:
            release_date = item['releaseDate']
        if not latest_revision_date or item['latestRevisionDate'] > latest_revision_date:
            latest_revision_date = item['latestRevisionDate']

    # Convert the release and revision dates to datetime objects
    release_date_obj = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
    revision_date_obj = datetime.fromisoformat(latest_revision_date.replace('Z', '+00:00'))
    # Convert the datetime objects to a string in the desired format
    release_date_str = release_date_obj.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
    release_date_str = release_date_str[:-2] + ':' + release_date_str[-2:]
    revision_date_str = revision_date_obj.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
    revision_date_str = revision_date_str[:-2] + ':' + revision_date_str[-2:]
    # Return the release and revision dates as strings in the desired format
    return release_date_str, revision_date_str

def update_vulnerabilities():
    """
    This function updates the existing set of vulnerabilities in 'vulnerabilities.json' by querying the Microsoft
    Security Update Guide API for any new or updated vulnerabilities since the last update.
    """
    # Get the latest release date and latest revision date from the vulnerabilities.json file
    release_date_str, revision_date_str = get_latest()
    # Set up the URL and query parameters for the Microsoft SUG API
    url = "https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability"
    querystring = {
        "$orderBy": "cveNumber desc",
        "$filter": f"(releaseDate gt {release_date_str} or latestRevisionDate gt {revision_date_str})"
    }
    # Set headers for the HTTP request
    headers = {
        "Accept": "application/json"
    }
    # Send a GET request to the Microsoft SUG API
    response = requests.get(url, headers=headers, params=querystring)
    # If the response is successful (status code 200), update the vulnerabilities.json file
    if response.status_code == 200:
        # Parse the response JSON data
        data = response.json()
        # Open the vulnerabilities.json file and add the new data to the existing data
        with open('vulnerabilities.json', 'r+') as f:
            current_data = json.load(f)
            current_data.extend(data['value'])
            f.seek(0)
            json.dump(current_data, f, indent=4)
            f.truncate()
        # Print a success message
        print("Vulnerabilities updated successfully!")
    else:
        # Print an error message if the request was not successful
        print(f"Error updating vulnerabilities: {response.status_code}")
    # Wait for 10 minutes before running the function again
    #await asyncio.sleep(600)
        
async def intial_vulnerabilities():
    """
    This function retrieves the initial set of vulnerabilities from the Microsoft Security Update Guide API
    and saves them to a local JSON file called 'vulnerabilities.json'.
    """
    while True:
        top = 200
        skip = 0
        vulnerabilitiesdata = []
        while True:
            if skip == 1000:
                break
            # Build the API URL with the $skip and $top parameters
            url = f"https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability?$skip={skip}&$top={top}"
            # Make the API request
            response = requests.get(url)
            # Check if there is any data returned
            if not response.content:
                break
            # Parse the JSON data
            data = json.loads(response.content)
            # Add the vulnerabilities to the list
            vulnerabilitiesdata.extend(data['value'])
            # Increment the skip counter
            skip += top

        with open('vulnerabilities.json', 'w') as f:
            json.dump(vulnerabilitiesdata, f)


@app.on_event("startup")
async def startup_event():
    """
    This function is a startup event for the FastAPI app.
    It is executed once at the start of the app.
    The function checks if the vulnerabilities.json file exists.
    If the file doesn't exist, it starts a new task for initializing the vulnerabilities data.
    The task is created using asyncio.create_task(), which schedules the task to be executed asynchronously.
    This ensures that the app can continue running while the task is being executed in the background.
    """
    if not os.path.exists("vulnerabilities.json"):
        asyncio.create_task(intial_vulnerabilities())

scheduler = BackgroundScheduler()
scheduler.add_job(update_vulnerabilities, 'interval', minutes=1)
scheduler.start()

#if __name__ == '__main__':
#    import uvicorn
#    uvicorn.run(app, host="127.0.0.1", port=8000)