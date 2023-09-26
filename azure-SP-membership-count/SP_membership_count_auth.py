from azure.identity import ClientSecretCredential
from azure.graphrbac import GraphRbacManagementClient

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
        self.graph_client = GraphRbacManagementClient(self.credential, tenant_id)

    def main(self):
        try:
            # Get the service principal details
            service_principal = self.graph_client.service_principals.get(service_principal_object_id)

            # Extract memberships count from app_roles
            app_roles = service_principal.app_roles
            membership_count = len(app_roles)

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
