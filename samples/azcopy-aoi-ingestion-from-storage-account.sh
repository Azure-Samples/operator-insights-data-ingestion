#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is an example bash script that demonstrates how to copy data from an Azure Storage Account to
# an Azure Operator Insights data product using the Azure CLI and the AzCopy tool.
# To use the script, fill in the variables at the top of the script and run it from the command line.
# 
# AzCopy can also copy data from other sources, such as Amazon Web Services S3 or Google Cloud Storage. See 
# https://learn.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-copy for examples.
# 
# TODO Check if it works on Windows and Linux.
# Pre-requisites: 
# - Log in to the Azure CLI ("az login") and set the subscription ("az account set --subscription <subscription>").
# - Install the network-analytics Azure CLI extension: "az extension add --name network-analytics"
# - Install the AzCopy tool and add the executable to your system path: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10 

set -euo pipefail
export AZCOPY_AUTO_LOGIN_TYPE=AZCLI

# Set variables for resource group, data product name, data type, and the URL of the files in the source
# Storage Account (including container and directory).
# Replace these values with your own.
rg="myResourceGroup"
dataProductName="myDataProduct"
dataType="myDataType"
sourceDataUrl="https://mysourceaccount.blob.core.windows.net/mycontainer/myBlobDirectory"

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

# Copy the files from the source Storage Account to the ingestion URL using AzCopy.
# This copies all files in $sourceDataUrl. See https://learn.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-copy
# for more options, including filtering.
# This fails if the identity used to run the script does not have permissions to read from the source Storage Account.
echo "Copying files from Azure Storage $sourceDataUrl to $ingestionUrl/$dataType/testdata/date-$(date +%d-%m-%Y)"
azcopy copy "$sourceDataUrl" "$ingestionUrl/$dataType/testdata/date-$(date +%d-%m-%Y)?$sasToken" --recursive=true
