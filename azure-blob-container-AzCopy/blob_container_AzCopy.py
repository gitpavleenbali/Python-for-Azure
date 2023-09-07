from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import ClientSecretCredential
import os, subprocess

# Declare all the variables required for the workflow
source_storage_account = "checkwithcharlie"
destination_storage_account = "testwithcharly2 "
keyword = "azcopy"
destination_container_name = "destination-azcopy"
service_principal_app_id = "c18d8674-0c22-411d-aa05-c96929a03cbe"
tenant_id = "d3bc2180-cb1e-40f7-b59a-154105743342"
client_secret = "c7P8Q~_D1O1PpSGK6AVTL3JkTzFn9txT.6aNSa2v"

# Set the AzCopy environment variables for service principal authentication
os.environ['AZCOPY_AUTO_LOGIN_TYPE'] = 'SPN'
os.environ['AZCOPY_SPA_APPLICATION_ID'] = service_principal_app_id
os.environ['AZCOPY_TENANT_ID'] = tenant_id
os.environ['AZCOPY_SPA_CLIENT_SECRET'] = client_secret

def find_containers_by_keyword(source_storage_account, keyword, service_principal_app_id, tenant_id, client_secret):
    # Create a client secret credential using the provided details
    client_secret_credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=service_principal_app_id,
        client_secret=client_secret
    )

    # Create a blob service client using the client secret credential
    account_url = f"https://{source_storage_account}.blob.core.windows.net"
    blob_service_client = BlobServiceClient(account_url=account_url, credential=client_secret_credential)

    # List all containers in the storage account
    container_names = []
    for container in blob_service_client.list_containers():
        if keyword in container['name']:
            container_names.append(container['name'])

    return container_names

def copy_data_between_containers(source_storage_account, destination_storage_account, source_container_names, destination_container_name):
    # Use AzCopy to copy data from the source to the destination container for each matching source container
    for source_container_name in source_container_names:
        azcopy_command = f"azcopy copy 'https://{source_storage_account}.blob.core.windows.net/{source_container_name}' 'https://{destination_storage_account}.blob.core.windows.net/{destination_container_name}' --recursive=true"
        try:
            subprocess.run(azcopy_command, shell=True, check=True)
            print(f"Data transfer completed successfully from {source_container_name} to {destination_container_name}")
        except subprocess.CalledProcessError as ex:
            print(f"Error while running AzCopy for container {source_container_name}: {ex}")

# Find containers with the specified keyword in both source storage account
source_container_names = find_containers_by_keyword(source_storage_account, keyword, service_principal_app_id, tenant_id, client_secret)

# Copy data from the matching source containers to the destination container within the destination storage account
if source_container_names:
    copy_data_between_containers(source_storage_account, destination_storage_account, source_container_names, destination_container_name)
else:
    print("No matching containers found.")
