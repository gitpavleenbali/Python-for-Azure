# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: blob_container_inventory.py
DESCRIPTION:
    This sample demonstrates how to create a customized blob container inventory for your blob storage using Python SDK for Azure. This tool
    helps to list important details like blob container name, its totla size and the name and size of each individual blob file in it.
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2) Instantiate 'credentia' method for authentication via Default Credential
    3) Instantiate a BlobServiceClient for the Storage-Account
    4) Create a workflow that suffices the current use-case as mentioned in the Description
"""

from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

account_url = "your_storage-account_url"
containerNames = ["container-blob-ver", "container-imt"]

class blob_container_inventory():

    def main(self):

        # Create Blob Service Client & use 'Default Credential' as the Authentication method via Terminal-Session log-in
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=_get_credential()
        )

        # Loop through the list of blob container names and get the size and number of blob files in each container
        for blob_container_name in containerNames:
            blob_container_client = blob_service_client.get_container_client(blob_container_name)
            total_container_size = 0

            # Initialize blob counter to 1
            blob_counter = 1

            # Print the name of the container, number of blob files in it & its total size
            blob_count = 0
            for _ in blob_container_client.list_blobs():
                blob_count += 1
            print('-' * 100)
            print("Blob Container Name: " + blob_container_name)
            print('-' * 100)
            print("Total Number of blob-files in it: " + str(blob_count))

            # Loop through the blobs in the container and get the size of each blob
            for blob in blob_container_client.list_blobs():
                blob_client = blob_service_client.get_blob_client(blob_container_name, blob.name)
                blob_props = blob_client.get_blob_properties()
                blob_size = blob_props.get('size', None)

                # Add the size of the blob to the total size
                total_container_size += blob_size

                # Get the name of the blob file with a counter
                blob_name = "Blob file " + str(blob_counter) + ": " + blob.name

                # Increment the blob counter
                blob_counter += 1

                # Print the name and size of the blob file
                print(blob_name)
                print("Size: " + str(blob_size) + " bytes")
            print('-' * 100)
            print("Total Size of the Blob Container: " + str(total_container_size) + " bytes")
            print('-' * 100)

            # Convert total_size to a string
            total_container_size_str = str(total_container_size)

            # Set the total_size as metadata for the blob container
            blob_container_client.set_container_metadata(metadata={'total_size': total_container_size_str + " bytes"})

        print()

def _get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential(
        exclude_managed_identity_credential=True,
        exclude_shared_token_cache_credential=True,
        exclude_visual_studio_code_credential=True,
        exclude_environment_credential=True,
        exclude_cli_credential=False,
        exclude_interactive_browser_credential=True,
    )

if __name__ == "__main__":
    run = blob_container_inventory()
    run.main()
