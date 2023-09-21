from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import ClientSecretCredential
import os, subprocess
from azure.core.exceptions import ClientAuthenticationError  # Import ClientAuthenticationError

# Declare all the variables required for the workflow
source_storage_account = ""
destination_storage_account = ""
dataset_keyword = "azcopy"
print("The filter-keyword used for identifying specific dataset is: " + dataset_keyword)
destination_container_name = ""
service_principal_app_id = ""
tenant_id = ""
client_secret = ""

# Set the AzCopy environment variables for service principal authentication
os.environ['AZCOPY_AUTO_LOGIN_TYPE'] = 'SPN'
os.environ['AZCOPY_SPA_APPLICATION_ID'] = service_principal_app_id
os.environ['AZCOPY_TENANT_ID'] = tenant_id
os.environ['AZCOPY_SPA_CLIENT_SECRET'] = client_secret
# Increase the performance of AzCopy
os.environ['AZCOPY_CONCURRENCY_VALUE'] = '1000'
#os.environ['AZCOPY_BUFFER_GB'] = '8'


# Create Credentials
def get_client_secret_credential(service_principal_app_id,
                                 tenant_id, client_secret):
    # Create a client secret credential using the provided details
    client_secret_credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=service_principal_app_id,
        client_secret=client_secret
    )
    return client_secret_credential


# Get the client secret credential
workflow_credential = get_client_secret_credential(service_principal_app_id,
                                                   tenant_id, client_secret)

# Define your AzCopy command template
azcopy_command_template = 'azcopy copy "https://{}.blob.core.windows.net/{}" "https://{}.blob.core.windows.net/{}" ' \
                          '--recursive=true --block-size-mb=16 --log-level=Info --overwrite=ifSourceNewer'


def find_containers_by_keyword(source_storage_account, dataset_keyword):
    # Create a blob service client using the client secret credential
    account_url = f"https://{source_storage_account}.blob.core.windows.net"
    blob_service_client = BlobServiceClient(account_url=account_url, credential=workflow_credential)

    # List all containers in the storage account
    container_names = []
    for container in blob_service_client.list_containers():
        if dataset_keyword in container['name']:
            container_names.append(container['name'])
    print("Filtered Containers are:")
    for name in container_names:
        print(name)
    return container_names


def copy_data_between_containers(source_storage_account, destination_storage_account, source_container_names,
                                 destination_container_name, folder_keyword=None):
    # Use AzCopy to copy data from the source to the destination container for each matching source container
    for source_container_name in source_container_names:

        # If a folder keyword is provided, copy folders within the dataset_keyword
        if folder_keyword:
            def copy_folders_with_keyword():
                # Create a blob service client using the client secret credential
                account_url = f"https://{source_storage_account}.blob.core.windows.net"
                blob_service_client = BlobServiceClient(account_url=account_url, credential=workflow_credential)

                # List all directories in the source container
                container_client = blob_service_client.get_container_client(source_container_name)
                blob_list = container_client.list_blobs()
                folder_names = set()

                # Extract unique folder names based on the keyword match
                for blob in blob_list:
                    blob_name = blob.name
                    if '/' in blob_name:
                        folder_name = blob_name.split('/')[0]
                        if folder_keyword in folder_name:
                            folder_names.add(folder_name)

                # Use AzCopy to copy data from matching folders in the source container to the destination container
                for folder_name in folder_names:
                    print("The name of the folder/directory getting copied is: " + folder_name)
                    azcopy_command = azcopy_command_template.format(
                        source_storage_account, f"{source_container_name}/{folder_name}", destination_storage_account,
                        f"{destination_container_name}/{dataset_keyword}")

                    try:
                        subprocess.run(azcopy_command, shell=True, check=True)
                        print(
                            f"Data transfer completed successfully from {source_container_name}/{folder_name} to {destination_container_name}")
                    except subprocess.CalledProcessError as ex:
                        print(f"Error while running AzCopy for folder {folder_name}: {ex}")

            # Call the folder copy function
            copy_folders_with_keyword()


# Find containers with the specified keyword in both source storage account
source_container_names = find_containers_by_keyword(source_storage_account, dataset_keyword)

# Copy data from the matching source containers to the destination container within the destination storage account
if source_container_names:
    copy_data_between_containers(source_storage_account, destination_storage_account, source_container_names,
                                 destination_container_name, folder_keyword="2020")
else:
    print("No matching containers found.")
