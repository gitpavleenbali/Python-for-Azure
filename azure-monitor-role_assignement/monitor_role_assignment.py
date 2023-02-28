# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: monitor_role_assignment.py
DESCRIPTION:
    This sample demonstrates how to monitor Role Base Access Control (RBAC) Limit on each subscription
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2)Instantiate the ServicePrincipalCredentials
    3) Instantiate the AuthorizationManagementClient

"""

from azure.mgmt.authorization import AuthorizationManagementClient
from azure.common.credentials import ServicePrincipalCredentials
tenant_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
application_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
application_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
sub_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
credSP = ServicePrincipalCredentials(client_id=application_id, secret=application_secret, tenant=tenant_id)
RB_List = []
threshold = 3500

def main():
    client = AuthorizationManagementClient(credentials=credSP, subscription_id=sub_id)
    roles = client.role_assignments.list()
    for role in roles:
        RB_List.append(role)
    if (len(RB_List)) < threshold:
        print('='*100)
        print("The current number of Role-Assignment for the Subscription is {}".format((len(RB_List))))
        print('=' * 100)
    else:
        raise Exception("Role-Assignments limit for the Subscription has Exceeded! Please Take Action Now!")

if __name__ == "__main__":
    main()