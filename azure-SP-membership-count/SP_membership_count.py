import requests
from azure.identity import DefaultAzureCredential
from tabulate import tabulate
import textwrap

# Enter the details of the service principal
service_principal_name = "Synapse Classic IAM"
service_principal_object_id = '7372d8fd-b5a5-4d63-a5fe-0d594df80bf5'

# Set the threshold for AAD Security-Group Memberships
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
            graph_url = f'https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_object_id}/memberOf'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(graph_url, headers=headers)

            if response.status_code == 200:
                # Parse the JSON response to get memberships and their names and types
                memberships = response.json().get('value', [])

                # Filter out only group memberships
                group_memberships = [membership for membership in memberships if
                                     membership.get('@odata.type') == '#microsoft.graph.group']

                return group_memberships
            else:
                print(f'Error retrieving memberships. Status code: {response.status_code}')
                return []

        except Exception as e:
            print(f'Error: {str(e)}')
            return []

    def get_group_memberships(self, group_id, access_token):
        try:
            # Make a request to the Microsoft Graph API to get the groups that the specified group is a member of
            graph_url = f'https://graph.microsoft.com/v1.0/groups/{group_id}/transitiveMemberOf'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(graph_url, headers=headers)

            if response.status_code == 200:
                # Parse the JSON response to get the groups that the group is a member of
                group_memberships = response.json().get('value', [])
                return group_memberships
            else:
                print(f'Error retrieving group memberships for group {group_id}. Status code: {response.status_code}')
                return []

        except Exception as e:
            print(f'Error: {str(e)}')
            return []

    # Declare the global variable
    count_non_redundant_combined_SG = 0
    def display_security_groups(self, memberships, access_token):
        global count_non_redundant_combined_SG  # Declare the variable as global
        try:
            # Create a list of lists for tabulate
            table_data = []
            complete_group_name = []
            complete_group_membership_names = []

            for membership in memberships:
                group_name = membership.get('displayName', 'N/A')
                group_id = membership.get('id')
                complete_group_name.append(group_name)

                # Get the groups that the security group is a member of
                group_memberships = self.get_group_memberships(group_id, access_token)

                # Count the AAD Security-Group memberships and Group Memberships
                group_membership_names = [group.get('displayName', 'N/A') for group in group_memberships]
                complete_group_membership_names.extend(group_membership_names)
                complete_group_membership_names = list(set(complete_group_membership_names))  # Remove duplicates

            # Calculate lengths
            main_sg_count = len(complete_group_name)
            nested_sg_count = len(complete_group_membership_names)

            # Join the complete_group_name and complete_group_membership_names with commas
            complete_group_name_str = ", ".join(complete_group_name)
            complete_group_membership_names_str = ", ".join(complete_group_membership_names)

            combined_SG = complete_group_name + complete_group_membership_names
            non_redundant_combined_SG = list(set(combined_SG))
            non_redundant_combined_SG_str = ", ".join(non_redundant_combined_SG)
            count_non_redundant_combined_SG = len(non_redundant_combined_SG)

            # Append data to the table
            table_data.append([service_principal_name,
                               "\n".join(textwrap.wrap(complete_group_name_str, width=30)),
                               main_sg_count,
                               "\n".join(textwrap.wrap(complete_group_membership_names_str, width=30)),
                               nested_sg_count,
                               "\n".join(textwrap.wrap(non_redundant_combined_SG_str, width=30)),
                               count_non_redundant_combined_SG])

            # Define table headers
            table_headers = ["Service Principal Name", "Main AAD Security-Groups \n(SGs)", "Main AAD SGs \n(Count)",
                             "Nested AAD SG \nGroup-Memberships \n(No Duplicates)", "Nested AAD SGs \nGroup-Memberships \n(Count)",
                             "Total Unique AAD SGs", "Total combined \nAAD SGs \n(Count)"]

            # Print the table using tabulate with a compact format
            table = tabulate(table_data, headers=table_headers, tablefmt="pretty", numalign="center")
            print(table)

        except Exception as e:
            print(f'Error: {str(e)}')

    def main(self):
        try:
            # Get the access token
            access_token = self.get_access_token()

            if access_token:
                # Get the memberships, their names, and types
                memberships = self.get_memberships(access_token)

                # Calculate the total membership count
                total_membership_count = sum(
                    len(self.get_group_memberships(group.get('id'), access_token)) + len(
                        [nested_group.get('displayName') for nested_group in
                         self.get_group_memberships(group.get('id'), access_token)])
                    for group in memberships
                )

                # Display security groups in a table, passing access_token as an argument
                self.display_security_groups(memberships, access_token)

                # Check if the count exceeds the threshold
                if total_membership_count > threshold:
                    raise Exception(
                        f"Alert: The Service-Principal's total AAD Security-Groups count of {count_non_redundant_combined_SG} exceeds the safe-threshold limit of {threshold}.")
                else:
                    print(
                        f"Alert: The Service-Principal's total AAD Security-Groups count is {count_non_redundant_combined_SG}, therefore it is within the safe-threshold limit of {threshold}.")

        except Exception as e:
            print(f'Error: {str(e)}')


if __name__ == "__main__":
    monitor = ServicePrincipalMembershipMonitor()
    monitor.main()
