import requests
from azure.identity import DefaultAzureCredential

# Define your Azure AD tenant ID and the service principal's object ID
tenant_id = "d3bc2180-cb1e-40f7-b59a-154105743342"
service_principal_object_id = "7372d8fd-b5a5-4d63-a5fe-0d594df80bf5"

# Initialize DefaultAzureCredential
credential = DefaultAzureCredential()

# Define the Microsoft Graph API endpoint to get the memberOf information
graph_url = f'https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_object_id}/memberOf'

# Acquire a token using managed identity
token = credential.get_token('https://graph.microsoft.com/.default')

headers = {
    'Authorization': f'Bearer {token.token}',
    'Content-Type': 'application/json'
}

# Make the API call to get the memberOf information
response = requests.get(graph_url, headers=headers)

if response.status_code == 200:
    group_data = response.json()
    num_groups = len(group_data.get('value', []))
    print(f'The service principal is a member of {num_groups} security groups.')
else:
    print(f'Failed to retrieve security group information. Status code: {response.status_code}')
    print(response.text)
