# -------------------------------------------------------------------------
# Copyright (c) gitpavleenbali
# --------------------------------------------------------------------------

"""
FILE: RG_DCAA.py
DESCRIPTION:
    This sample demonstrates container operations for enabling blob data immutability policy for business-critical data.
USAGE:
    Define the required utilities for the current workflow
    1) Define all the required variables
    2) Instantiate "_get_credential()" method via DefaultAzureCredential
    3) Instantiate the CostManagementClient
    4) Instantiate the "get_query_definition" method
    5) Instantiate the "query_definition" object for calculating last-week cost, this-week cost & total-current cost

"""

import csv, logging, sys
import tabulate
from time import sleep
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition, QueryDataset, QueryFilter, QueryComparisonExpression, \
    QueryAggregation
from datetime import date
today = date.today()
date = today.strftime("%B %d, %Y")

# threshold-value in percentage
threshold = 20
RG_List = []
Sub_ID_List = []
result_file = open('../result/result_RG_DCAA.txt', 'w')
result_file.close()
filename = open('../utility/RG_List.csv', 'r')
file = csv.DictReader(filename)

for rg in file:
    RG_List.append(rg['rgName'])
    Sub_ID_List.append(rg['subscriptionId'])

def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    client = CostManagementClient(credential=_get_credential())
    query_definition_total_current_cost = get_query_definition("BillingMonthToDate")
    query_definition_last_week_cost = get_query_definition("TheLastWeek")
    query_definition_this_week_cost = get_query_definition("WeekToDate")

    scope = "/subscriptions/" + Sub_ID_List[0]

    try:
        result_total_current_cost = client.query.usage(scope=scope, parameters=query_definition_total_current_cost)
        sorted_result = sorted(result_total_current_cost.rows, key=lambda kv: kv[1])
        total_current_cost = sorted_result[0][0]
        sleep(1)
        result_last_week_cost = client.query.usage(scope=scope, parameters=query_definition_last_week_cost)
        sorted_result = sorted(result_last_week_cost.rows, key=lambda kv: kv[1])
        last_week_cost = sorted_result[0][0]
        sleep(1)
        result_this_week_cost = client.query.usage(scope=scope, parameters=query_definition_this_week_cost)
        sorted_result = sorted(result_this_week_cost.rows, key=lambda kv: kv[1])
        this_week_cost = sorted_result[0][0]
        sleep(1)

        percent_fraction = (((this_week_cost / last_week_cost) - 1) * 100)

        data = [[date, "Azure Weekly-Cost", "Azure Subscription for Demo", "RG with tag 'demo:psbali'", total_current_cost, last_week_cost,
                 this_week_cost, percent_fraction]]

        # define header names
        col_names = ["Date", "Type", "Subscription", "Azure-Resource", "This-Month Amount (€)",
                     "Last-Week Amount (€)", "This-Week Amount (€)", "% Utilization compared to Last-Week"]

        # display table
        cost_table = tabulate.tabulate(data, headers=col_names, tablefmt="fancy_grid")
        print(cost_table)

        with open('../result/result_RG_DCAA.txt', 'a', encoding='utf-8') as file:
            file.write(cost_table)

        if percent_fraction < threshold:
            print("Cost is under Control")
        else:
            raise Exception("Cost Exceeded! Take Action!")

        print('Workflow Succeeded, Results are Available as of Now!!')

    except IndexError:
        print('!!Workflow Failed, No Results are Available as of Now!!')

def _get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential(
        exclude_managed_identity_credential=True,
        exclude_shared_token_cache_credential=True,
        exclude_visual_studio_code_credential=True,
        exclude_environment_credential=True,
        exclude_cli_credential=False,
        exclude_interactive_browser_credential=True,
    )

def get_query_definition(value) -> QueryDefinition:
    query_dataset = QueryDataset(
        granularity="weekly",
        filter=QueryFilter(dimensions=QueryComparisonExpression(name="ResourceGroup", operator="In", values=RG_List)),
        aggregation={"totalCost": QueryAggregation(name="PreTaxCost", function="Sum")}
    )
    return QueryDefinition(type="Usage", timeframe=value, dataset=query_dataset)


if __name__ == "__main__":
    main()
