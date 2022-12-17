# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: blob_versioning.py
DESCRIPTION:
    This sample demonstrates ADLS storage-operations for enabling blob-versioning to keep track of historical data
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2) Instantiate a BlobServiceClient for the Storage-Account
    3) Instantiate a ContainerClient for the Container
    4) Instantiate a StorageManagementClient for Blob Versioning
    5) Instantiate a BlobClient for the specific Blob
"""

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from azure.mgmt.storage import StorageManagementClient

# Define the required variables for the current workflow
account_url = "https://demo00blobversioning.blob.core.windows.net/"
rgName = "RG_Demo_ADLS_Data_Protection"
staName = "demo00blobversioning"
containerName = "container-blob-versioning"


class blob_versioning():

    def main(self):

        # Instantiate a BlobServiceClient for the Storage-Account
        container_client = BlobServiceClient(
            account_url=account_url,
            credential=_get_credential()
        )

        # Instantiate a ContainerClient for the Container
        container_client_blob = ContainerClient(
            account_url=account_url,
            container_name=containerName,
            credential=_get_credential()
        )

        # Create a Container
        try:
            container = container_client.create_container(name=containerName)
            if container:
                print('-' * 100)
                print('Container %s created' % (containerName))
                print('-' * 100)
        except ResourceExistsError:
            pass

        # Create a new Blob & Upload a dummy-file to the BLOB
        try:
            with open("dummy_blob.txt", "rb") as blob_file:
                _blob_client().upload_blob(data=blob_file)
        except ResourceExistsError:
            pass

        # Instantiate a StorageManagementClient for Blob Versioning
        container_client_versioning = StorageManagementClient(
            credential=_get_credential(),
            subscription_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', # Please enter Your Subscription ID
            base_url="https://management.azure.com"

        )

        # Instantiate a BlobClient for the specific blob
        blob_client = container_client.get_blob_client(
            container=containerName, blob="blob-versioning"
        )

        # Enable Blob Versioning [Feature Still in Preview]
        try:
            container_client_versioning.blob_services.set_service_properties(rgName, staName,
                                                                             {'is_versioning_enabled': True,
                                                                              })
        except Exception as e:
            print(e)
            pass

        # Again write with the same dummy-file on to the same Blob with parameter "overwrite=True"
        try:
            with open("dummy_blob.txt", "rb") as blob_file:
                _blob_client().upload_blob(data=blob_file, overwrite=True)
        except ResourceExistsError:
            pass

        # Verify Blob Versioning
        blob_property = blob_client.get_blob_properties()
        blob_verID = blob_property['version_id']
        print('-' * 100)
        print("The blob version ID is {}".format(blob_verID))
        if blob_verID != 0:
            print("Blob Versioning Validation Successful!!")
        else:
            print('Blob Versioning not Enabled!!')
        print('-' * 100)


def _get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential(
        exclude_managed_identity_credential=True,
        exclude_shared_token_cache_credential=True,
        exclude_visual_studio_code_credential=True,
        exclude_environment_credential=True,
        exclude_cli_credential=False,
        exclude_interactive_browser_credential=True,
    )


# Create a BlobClient for the uploading the BLOB
def _blob_client():
    blob_name = "blob-versioning"
    blob_url = f"{account_url}/{containerName}/{blob_name}"

    try:
        blob_client = BlobClient.from_blob_url(
            blob_url=blob_url,
            credential=_get_credential()
        )
    except ResourceExistsError:
        pass
    return blob_client


if __name__ == "__main__":
    imt = blob_versioning()
    imt.main()
