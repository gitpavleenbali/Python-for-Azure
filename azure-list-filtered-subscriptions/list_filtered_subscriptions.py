# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: list_filtered_subscriptions.py
DESCRIPTION:
    This sample demonstrates how to filter and list azure subscriptions based on specific keyword.
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2) Instantiate 'credentia' method for authentication via Default Credential
    3) Create a workflow that suffices the current use-case as mentioned in the Description
"""

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient

def get_subscriptions_with_keyword(keyword):
    # Authenticate using DefaultAzureCredential
    credentials = _get_credential()

    # Create a SubscriptionClient instance
    subscription_client = SubscriptionClient(credentials)

    # Get a list of subscriptions
    subscriptions = list(subscription_client.subscriptions.list())

    # Filter subscriptions containing the keyword in the subscription name
    matching_subscriptions = [
        {"id": sub.subscription_id, "name": sub.display_name}
        for sub in subscriptions
        if keyword.lower() in sub.display_name.lower()
    ]

    return matching_subscriptions

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
    keyword_filter = "data"  # Replace "data" with your desired keyword
    matching_subscriptions = get_subscriptions_with_keyword(keyword_filter)

    if not matching_subscriptions:
        print(f"No subscriptions found containing the keyword '{keyword_filter}'.")
    else:
        print("Matching subscriptions:")
        for sub in matching_subscriptions:
            print(f"Subscription Name: {sub['name']}, Subscription ID: {sub['id']}")