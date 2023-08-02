from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError, ResourceExistsError

def check_container_access(storage_account_name, container_name, service_principal_app_id, tenant_id, client_secret):
    # Create a client secret credential using the provided details
    client_secret_credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=service_principal_app_id,
        client_secret=client_secret
    )

    # Create a blob service client using the client secret credential
    account_url = f"https://{storage_account_name}.blob.core.windows.net"
    blob_service_client = BlobServiceClient(account_url=account_url, credential=client_secret_credential)
    container_client = blob_service_client.get_container_client(container_name)
    print(f"Service principal APP-ID: {service_principal_app_id}")

    # Check READ-ACCESS
    read_access = False
    try:
        test_read_access = container_client.list_blobs()
        total_blobs = sum(1 for _ in test_read_access)
        if total_blobs > 0:
            read_access = True
            print("The service principal has READ-ACCESS to the container.")
    except HttpResponseError as ex:
        if ex.status_code == 404:
            print("The specified container does not exist.")
        elif ex.status_code == 403:
            print("The service principal does not have READ-ACCESS to the container.")
        else:
            print(f"An error occurred while checking READ-ACCESS: {ex}")

    # Check WRITE-ACCESS
    write_access = False
    test_blob_name = "test_write_access.txt"
    try:
        blob_client = container_client.get_blob_client(test_blob_name)
        blob_client.upload_blob("This is a test.")
        write_access = True
        blob_client.delete_blob()  # Delete the test blob if it was created successfully
        print("The service principal has WRITE-ACCESS to the container.")
    except HttpResponseError as ex:
        if ex.status_code == 403:
            print("The service principal does not have WRITE-ACCESS to the container.")
        else:
            print(f"An error occurred while checking WRITE-ACCESS: {ex}")

    # Output the results
    print(f"READ-ACCESS: {read_access}")
    print(f"WRITE-ACCESS: {write_access}")

# Replace these with your actual values
storage_account_name = "st1awesteuautanadev001"
container_name = "anonymization"
service_principal_app_id = "c18d8674-0c22-411d-aa05-c96929a03cbe"
tenant_id = "d3bc2180-cb1e-40f7-b59a-154105743342"
client_secret = "c7P8Q~_D1O1PpSGK6AVTL3JkTzFn9txT.6aNSa2v"

check_container_access(storage_account_name, container_name, service_principal_app_id, tenant_id, client_secret)
