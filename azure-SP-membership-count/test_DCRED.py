import requests
from azure.identity import DefaultAzureCredential
from tabulate import tabulate

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
    security_groups = group_data.get('value', [])

    print(f'The Service-Principal is a member of the following AAD Security-Groups:')

    # Create a list of lists for tabulate
    table_data = []

    for index, group in enumerate(security_groups, start=1):
        group_name = group['displayName']
        table_data.append([index, group_name])

    # Define table headers
    table_headers = ["S.No.", "Security Group Name"]

    # Print the table using tabulate
    print(tabulate(table_data, headers=table_headers, tablefmt="fancy_grid"))

    num_groups = len(security_groups)

    # Set a threshold for the number of security groups
    threshold = 175

    if num_groups > threshold:
        raise Exception(f'Alert: The Service-Principal current AAD Security-Groups membership count of {num_groups} exceeds the safe-threshold limit of {threshold}.')
    else:
        print(
            f'Alert: The Service-Principal current AAD Security-Groups membership count of {num_groups} is within safe-threshold limit.')
else:
    print(f'Failed to retrieve security group information. Status code: {response.status_code}')
    print(response.text)
