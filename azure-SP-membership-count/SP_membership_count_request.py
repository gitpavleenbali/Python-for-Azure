import requests
from azure.identity import ClientSecretCredential

# Replace with your Azure AD tenant ID, client ID, and client secret
tenant_id = "d3bc2180-cb1e-40f7-b59a-154105743342"
client_id = "c18d8674-0c22-411d-aa05-c96929a03cbe"
client_secret = "c7P8Q~_D1O1PpSGK6AVTL3JkTzFn9txT.6aNSa2v"

# Replace with the object ID of your service principal
service_principal_object_id = '7372d8fd-b5a5-4d63-a5fe-0d594df80bf5'

# Set the threshold
threshold = 175

class ServicePrincipalMembershipMonitor:

    def __init__(self):
        self.credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    def get_access_token(self):
        # Get an access token using the service principal's credentials
        token = self.credential.get_token("https://graph.microsoft.com/.default")
        return token.token

    def main(self):
        try:
            # Get the access token
            access_token = self.get_access_token()

            # Make a request to the Graph API to get the service principal's details
            graph_url = f'https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_object_id}'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(graph_url, headers=headers)

            if response.status_code == 200:
                # Extract memberships count from the response (you may need to parse the JSON response)
                membership_count = 0  # Implement parsing logic here

                # Check if the count exceeds the threshold
                if membership_count > threshold:
                    print(f'Service principal exceeded membership threshold. Current count: {membership_count}')
                    # Implement alerting logic here (e.g., send an email)
                else:
                    print(f'Membership count within threshold. Current count: {membership_count}')
            else:
                print(f'Error retrieving service principal details. Status code: {response.status_code}')

        except Exception as e:
            print(f'Error: {str(e)}')

if __name__ == "__main__":
    monitor = ServicePrincipalMembershipMonitor()
    monitor.main()
