#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is an example bash script that demonstrates how to upload data to an Azure Operator Insights 
# data product using the Azure CLI.
# To use the script, fill in the variables at the top of the script and run it from the command line.
# 
# TODO Check if it works on Windows and Linux.
# Pre-requisites: 
# - Log in to the Azure CLI ("az login") and set the subscription ("az account set --subscription <subscription>").
# - Install the network-analytics Azure CLI extension: "az extension add --name network-analytics".

set -euo pipefail

# Set variables for resource group, data product name, data type, and the local filepath of the files to upload.
# Replace these values with your own.
rg="myResourceGroup"
dataProductName="myDataProduct"
dataType="myDataType"
sourceDataFilePath="path/to/local/dir"

# Use the data product API to get the ingestion URL.
ingestionUrl=$(az network-analytics data-product show --name $dataProductName --resource-group $rg --query consumptionEndpoints.ingestionUrl --output tsv)

# Break out the data product ID and the storage account name from the ingestion URL.
# If the ingestion URL is "https://aoiingestion1234abcd.blob.core.windows.net", then the data 
# product ID is "1234abcd" and the storage account name is "aoiingestion1234abcd".
dataProductId=$(echo "$ingestionUrl" | sed -n 's/https:\/\/aoiingestion\(.*\).blob.core.windows.net/\1/p')

# Use the data product ID to generate the name of the managed key vault
keyVaultName="aoi-$dataProductId-kv"

# Fetch the SAS URL from the key vault, and extract the SAS token from the URL. 
# The SAS token is everything after the '?' character.
# This fails if the identity used to run the script does not have at least "Key Vault Secrets User" permissions on the key vault.
echo "Fetching SAS URL from key vault $keyVaultName"
sasUrl=$(az keyvault secret show --vault-name "$keyVaultName" --name input-storage-sas --query "value" --output tsv)
sasToken=$(echo "$sasUrl" | sed -n 's/.*?//p')

# Copy the files in sourceDataFilePath to the ingestion URL using az storage CLI command
# This copies all files in $sourceDataFilePath. See https://learn.microsoft.com/en-us/cli/azure/storage/blob?view=azure-cli-latest#az-storage-blob-upload-batch 
# for more options, including filtering.
echo "Uploading files from local path $sourceDataFilePath"
az storage blob upload-batch --blob-endpoint "$ingestionUrl" --source $sourceDataFilePath --destination "$dataType" --destination-path "testdata/date-$(date +%d-%m-%Y)" --sas-token "$sasToken" --output none
