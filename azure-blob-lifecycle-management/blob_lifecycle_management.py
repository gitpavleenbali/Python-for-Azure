# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: blob_lifecycle_management.py
DESCRIPTION:
    This sample demonstrates blob lifecycle management (LCM) which offers a rule-based policy that you can use to
    transition blob data to the appropriate access tiers or to expire data at the end of the data lifecycle.
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2) Instantiate a BlobServiceClient for the Storage-Account
    3) Instantiate a ContainerClient for the Container
    4) Instantiate a StorageManagementClient for Data LCM & Purge Policy
"""

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from azure.mgmt.storage import StorageManagementClient

# Define the required variables for the current workflow
account_url = "https://demo00bloblcmpurge.blob.core.windows.net/"
rgName = "RG_Demo_ADLS_Data_LCM"
staName = "demo00bloblcmpurge"
containerName = "container-lcm-purge"
POLICY_NAME = "default"


class data_purge_lcm_poliy():

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

        # Instantiate a ContainerClient for Data LCM & Purge Policy
        container_client = StorageManagementClient(
            credential=_get_credential(),
            subscription_id='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', # Please enter Your Subscription ID
            base_url="https://management.azure.com"

        )

        # Create Data Lifecycle Management Policy for Automated Access-Tier & Purge of Data
        management_policy = container_client.management_policies.create_or_update(
            rgName,
            staName,
            POLICY_NAME,
            {
                "policy": {
                    "rules": [
                        {
                            "enabled": True,
                            "name": "test-python-lcm-rules",
                            "type": "Lifecycle",
                            "definition": {
                                "filters": {
                                    "blob_types": [
                                        "blockBlob"
                                    ],
                                    "prefix_match": [
                                        "container-lcm-purge"
                                    ]
                                },
                                "actions": {
                                    "base_blob": {
                                        "tier_to_cool": {
                                            "days_after_modification_greater_than": "150"
                                        },
                                        "tier_to_archive": {
                                            "days_after_modification_greater_than": "300"
                                        },
                                        # This is to purge data based on the rule specified
                                        "delete": {                                                    #
                                            "days_after_modification_greater_than": "600"
                                        }
                                    },
                                }
                            }
                        }
                    ]
                }
            }
        )
        print('-' * 100)
        print("Data Lifecycle Management Policy Created & Applied")
        print('-' * 100)

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
    imt = data_purge_lcm_poliy()
    imt.main()
