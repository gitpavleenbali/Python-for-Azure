import requests
from azure.identity import DefaultAzureCredential

# Replace with your Azure AD tenant ID
tenant_id = "d3bc2180-cb1e-40f7-b59a-154105743342"

# Replace with the object ID of your service principal
service_principal_object_id = '7372d8fd-b5a5-4d63-a5fe-0d594df80bf5'

# Set the threshold
threshold = 175

# Replace with your alerting logic here (e.g., send an email)
def create_alert(message):
    print(f"Alert: {message}")

class ServicePrincipalSecurityGroupFinder:

    def __init__(self):
        self.credential = DefaultAzureCredential()

    def get_access_token(self):
        # Get an access token using DefaultAzureCredential
        token = self.credential.get_token("https://graph.microsoft.com/.default")
        return token.token

    def get_security_groups(self, access_token):
        try:
            # Make a request to the Microsoft Graph API to get the app role assignments for the service principal
            graph_url = f'https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_object_id}/appRoleAssignedTo'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(graph_url, headers=headers)

            if response.status_code == 200:
                # Parse the JSON response to get the app role assignments
                app_role_assignments = response.json().get('value', [])
                security_groups = []

                for assignment in app_role_assignments:
                    principal_type = assignment.get('principalType')
                    principal_display_name = assignment.get('principalDisplayName')
                    if principal_type == 'SecurityGroup':
                        security_groups.append(principal_display_name)

                return security_groups
            else:
                print(f'Error retrieving app role assignments. Status code: {response.status_code}')
                return []

        except Exception as e:
            print(f'Error: {str(e)}')
            return []

    def main(self):
        try:
            # Get the access token
            access_token = self.get_access_token()

            if access_token:
                # Get the security groups where the service principal is assigned a role
                security_groups = self.get_security_groups(access_token)

                if security_groups:
                    print(f'Service principal is a member of {len(security_groups)} security groups:')
                    for group in security_groups:
                        print(group)

                    # Check if the count exceeds the threshold
                    if len(security_groups) > threshold:
                        create_alert("Service principal exceeded security group threshold. Membership count is not under control.")
                    else:
                        create_alert("Service principal membership count is under control.")
                else:
                    # No security groups found
                    create_alert("Service principal is not a member of any security group.")

        except Exception as e:
            print(f'Error: {str(e)}')

if __name__ == "__main__":
    finder = ServicePrincipalSecurityGroupFinder()
    finder.main()