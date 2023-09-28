import requests
from azure.identity import DefaultAzureCredential

# Replace with your Azure AD tenant ID
tenant_id = "d3bc2180-cb1e-40f7-b59a-154105743342"

# Replace with the object ID of your service principal
service_principal_object_id = '7372d8fd-b5a5-4d63-a5fe-0d594df80bf5'

# Set the threshold
threshold = 175

class ServicePrincipalMembershipMonitor:

    def __init__(self):
        self.credential = DefaultAzureCredential()

    def get_access_token(self):
        # Get an access token using DefaultAzureCredential
        token = self.credential.get_token("https://graph.microsoft.com/.default")
        return token.token

    def get_memberships(self, access_token):
        try:
            # Make a request to the Microsoft Graph API to get the service principal's memberships
            graph_url = f'https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_object_id}/appRoleAssignedTo'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(graph_url, headers=headers)

            if response.status_code == 200:
                # Parse the JSON response to get memberships and their names and types
                memberships = response.json().get('value', [])
                return memberships
            else:
                print(f'Error retrieving memberships. Status code: {response.status_code}')
                return []

        except Exception as e:
            print(f'Error: {str(e)}')
            return []

    def main(self):
        try:
            # Get the access token
            access_token = self.get_access_token()

            if access_token:
                # Get the memberships, their names, and types
                memberships = self.get_memberships(access_token)

                # Count the memberships
                membership_count = len(memberships)

                # Create a list to store membership details
                membership_details = []

                for membership in memberships:
                    principal_display_name = membership.get('principalDisplayName', 'N/A')
                    principal_type = membership.get('principalType', 'N/A')
                    membership_details.append(f'{principal_display_name} ({principal_type})')

                print(f'Membership count: {membership_count}')
                print(f'Membership details: {", ".join(membership_details)}')

                # Check if the count exceeds the threshold
                if membership_count > threshold:
                    print(f'Service principal exceeded membership threshold. Current count: {membership_count}')
                    # Implement alerting logic here (e.g., send an email)
                else:
                    print(f'Membership count within threshold. Current count: {membership_count}')

        except Exception as e:
            print(f'Error: {str(e)}')

if __name__ == "__main__":
    monitor = ServicePrincipalMembershipMonitor()
    monitor.main()