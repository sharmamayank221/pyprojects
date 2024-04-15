import requests
import os
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# Define the API endpoint and access token
url = "https://api.webflow.com/v2/sites/636b01f4514fce58703fb4a8/collections/65fd013b82c9e08915e38117/items"
access_token = os.getenv('WEBFLOW_ACCESS_TOKEN')

# Ensure the access token is not empty
if not access_token:
    raise ValueError("Webflow access token is not set.")

# Define the headers (including the access token)
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Load the JSON content from the file
with open('document_content.json', 'r') as file:
    json_content = file.read()

# Make the POST request
response = requests.post(url, headers=headers, data=json_content)

# Check if the request was successful
if response.status_code == 202:
    print("JSON content uploaded successfully to Webflow CMS.")
else:
    print(f"Error uploading JSON content: {response.status_code} - {response.text}")
