# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: blob_snapshot.py
DESCRIPTION:
    This sample demonstrates ADLS blob-operations to create blob-snapshot to keep track of historical data on blob file
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2) Instantiate a BlobServiceClient for the Storage-Account
    3) Instantiate a ContainerClient for the Container
    4) Instantiate a StorageManagementClient for Blob Snapshot
    5) Instantiate a BlobClient for the specific Blob
"""

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from azure.mgmt.storage import StorageManagementClient

# Define the required variables for the current workflow
account_url = "https://demo00blobsnapshot.blob.core.windows.net/"
rgName = "RG_Demo_ADLS_Data_Protection"
staName = "demo00blobsnapshot"
containerName = "container-blob-snapshot"


class blob_snapshot():

    def main(self):

        # Instantiate a BlobServiceClient for the Container
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
            with open("utils/snapshot_blob.txt", "rb") as blob_file:
                _blob_client().upload_blob(data=blob_file)
        except ResourceExistsError:
            pass

        # Instantiate a BlobClient for the specific blob
        blob_client = container_client.get_blob_client(
            container=containerName, blob="test_00/snapshot_blob.txt"
        )

        # Instantiate a ContainerClient for Blob
        container_client_snapshot = StorageManagementClient(
            credential=_get_credential(),
            subscription_id='4de57da5-98b6-4452-905b-7aa96bcfec50',
            base_url="https://management.azure.com"

        )

        # Enable Automatic Snapshot Policy
        try:

            container_client_snapshot.blob_services.set_service_properties(rgName, staName,
                                                                           {
                                                                               'automatic_snapshot_policy_enabled:': True})

            # Create a snapshot of the blob
            for i in range(5):
                blob_snapshot = blob_client.create_snapshot()
                print('-' * 100)
                print('Blob Snapshot Successfully Created')
                print("The time-stamp of the latest blob-snapshot is {}".format(blob_snapshot.get('snapshot')))
                print('-' * 100)


        except Exception as e:
            print(e)
            pass


# Create Azure credential method for AD Authentication
def _get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential(
        exclude_managed_identity_credential=True,
        exclude_shared_token_cache_credential=True,
        exclude_visual_studio_code_credential=True,
        exclude_environment_credential=True,
        exclude_cli_credential=False,
        exclude_interactive_browser_credential=True,
    )


# Create a BlobClient for the BLOB
def _blob_client():
    blob_name = "blob-01"
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
    imt = blob_snapshot()
    imt.main()
