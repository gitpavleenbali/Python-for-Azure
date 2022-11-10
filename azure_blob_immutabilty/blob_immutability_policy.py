# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: blob_immutability_policy.py
DESCRIPTION:
    This sample demonstrates container operations for enabling blob data immutabilty policy for business-critical data.
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2) Instantiate a BlobServiceClient for the Container
    3) Instantiate a ContainerClient for the Container
    4) Instantiate a ContainerClient for Immutability Policy implementation
"""

from azure.core.exceptions import ResourceExistsError, HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import LegalHold

# Define the required variables for the current workflow
account_url = "https://demo00immutability.blob.core.windows.net/"
rgName = "RG_Demo_Immutablity"
staName = "demo00immutability"
containerName = "container-imt-policy"


class container_immutability():

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
            with open("dummy_blob.txt", "rb") as blob_file:
                _blob_client().upload_blob(data=blob_file)
        except ResourceExistsError:
            pass

        # Read the content of the file of the blob before immutability workflow
        pre_workflow = read_blob_content('pre_workflow')

        # Instantiate a ContainerClient for Immutability
        container_client_immutability = StorageManagementClient(
            credential=_get_credential(),
            subscription_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', # Please enter Your Subscription ID
            base_url="https://management.azure.com"

        )

        # Set LegalHold immutability policy on the container [Layer-I Protection]
        legal_hold = LegalHold(tags=['tstImmutability'])
        try:
            container_client_immutability.blob_containers.set_legal_hold(rgName, staName, containerName,
                                                                         legal_hold)

        except HttpResponseError as e:
            print(e)
            pass

        # Try to delete the container to validate Layer-I Protection 
        try:
            container_client_blob.delete_container()
        except ResourceExistsError as e:
            print('**Note**: The container cannot be deleted after Immutability enabled')
            print(e)
            pass

        # Read the content of the file of the blob after immutability & deletion workflow
        after_workflow = read_blob_content('after_workflow')

        # Validate whether immutabilty policy has worked or not
        if pre_workflow == after_workflow:
            print("**Note**: Contents of the BLOB are Unchanged. Immutability Successfully Validated")
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


# Create a BlobClient for the BLOB
def _blob_client():
    blob_name = "blob-immutability"
    blob_url = f"{account_url}/{containerName}/{blob_name}"

    try:
        blob_client = BlobClient.from_blob_url(
            blob_url=blob_url,
            credential=_get_credential()
        )
    except ResourceExistsError:
        pass
    return blob_client


# Read the content of the BLOB
def read_blob_content(message):
    blob_download = _blob_client().download_blob()
    blob_content = blob_download.readall().decode("utf-8")
    print('-' * 100)
    print("The content of the Blob {0} is as under:".format(message))
    print(blob_content)
    print('-' * 100)


if __name__ == "__main__":
    imt = container_immutability()
    imt.main()
