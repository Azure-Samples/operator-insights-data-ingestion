#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is an example bash script that demonstrates how to use the Azure CLI to set up the required 
# parameters before uploading data to an Azure Operator Insights data product.
# To use the script, fill in the variables at the top of the script and run it from the command line
# using the source command, passing in your resource group and data product name as parameters, 
# e.g. "source az-cli-set-ingestion-params.sh myResourceGroup myDataProduct". Alternatively, call 
# this script from another script using the source command.
# The script sets the following environment variables, which can be used in a separate upload script 
# or as input to a tool like AzCopy:
# - INGESTION_URL: The ingestion URL for the data product. 
# - INGESTION_STORAGE_ACCOUNT_NAME
# - INGESTION_SAS_TOKEN: The SAS token for the data product ingestion storage account.
# 
# Most ingestion methods will require the INGESTION_SAS_TOKEN and either INGESTION_URL or 
# INGESTION_STORAGE_ACCOUNT_NAME.
# 
# Pre-requisites: 
# - Log in to the Azure CLI ("az login") and set the subscription ("az account set --subscription <subscription>").
# - Install the network-analytics Azure CLI extension: "az extension add --name network-analytics".

set -euo pipefail

# Set variables for resource group and data product name.
resourceGroup=$1
dataProductName=$2

# Use the data product API to get the ingestion URL.
ingestionUrl=$(az network-analytics data-product show --name "$dataProductName" --resource-group "$resourceGroup" --query consumptionEndpoints.ingestionUrl --output tsv)

# Break out the data product ID from the ingestion URL.
# If the ingestion URL is "https://aoiingestiondp123abc.blob.core.windows.net", then the data 
# product ID is "dp123abc" and the storage account name is "aoiingestiondp123abc".
dataProductId=$(echo "$ingestionUrl" | sed -n 's/https:\/\/aoiingestion\(.*\).blob.core.windows.net/\1/p')

# Use the data product ID to generate the name of the managed key vault
keyVaultName="aoi-$dataProductId-kv"

# Fetch the SAS URL from the key vault, and extract the SAS token from the URL. 
# The SAS token is everything after the '?' character.
# This fails if the identity used to run the script does not have at least "Key Vault Secrets User" permissions on the key vault.
echo "Fetching SAS URL from key vault $keyVaultName"
sasUrl=$(az keyvault secret show --vault-name "$keyVaultName" --name input-storage-sas --query "value" --output tsv)
sasToken=$(echo "$sasUrl" | sed -n 's/.*?//p')

# Set environment variables for the ingestion URL, storage account name, and SAS token.
export INGESTION_URL=$ingestionUrl
export INGESTION_STORAGE_ACCOUNT_NAME="aoiingestion$dataProductId"
export INGESTION_SAS_TOKEN=$sasToken
