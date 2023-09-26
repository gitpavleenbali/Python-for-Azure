from azure.identity import DefaultAzureCredential
from azure.graphrbac import GraphRbacManagementClient
from azure.graphrbac.models import Application
import requests

# Replace with your Azure AD tenant ID, client ID, and client secret
tenant_id = "d3bc2180-cb1e-40f7-b59a-154105743342"
client_id = "c18d8674-0c22-411d-aa05-c96929a03cbe"
client_secret = "c7P8Q~_D1O1PpSGK6AVTL3JkTzFn9txT.6aNSa2v"

# Threshold for membership count
threshold = 175


# Microsoft Graph API endpoint to get application (service principal) details
graph_url = f"https://graph.microsoft.com/v1.0/applications?$filter=appId eq '{client_id}'"

# Define the headers for making the request
headers = {
    "Content-Type": "application/json",
}

# Define the payload for requesting an access token
token_payload = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": f"https://graph.microsoft.com/.default",
}

try:
    # Request an access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_response = requests.post(token_url, data=token_payload)
    token_data = token_response.json()
    access_token = token_data.get("access_token")

    # Use the access token to make a request to the Microsoft Graph API
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.get(graph_url, headers=headers)

        if response.status_code == 200:
            application_data = response.json()
            membership_count = application_data.get("value")[0].get("appRolesAssignedCount")

            print(f"Membership count for Service Principal: {membership_count}")

            if membership_count > threshold:
                print("Alert: Membership count exceeds threshold!")
            else:
                print("Membership count is within the threshold.")
        else:
            print(f"Error: Unable to retrieve application data - {response.status_code} - {response.text}")
    else:
        print("Error: Unable to obtain an access token.")
except Exception as e:
    print(f"Error: {str(e)}")