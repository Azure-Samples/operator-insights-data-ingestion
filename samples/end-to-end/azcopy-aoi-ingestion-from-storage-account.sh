#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is an example bash script that demonstrates how to copy data from an Azure Storage Account to
# an Azure Operator Insights Data Product using the Azure CLI and the AzCopy tool.
# To use the script, fill in the variables at the top of the script and run it from the command line.
# 
# AzCopy can also copy data from other sources, such as Amazon Web Services S3 or Google Cloud Storage. See 
# https://learn.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-copy for examples.
# 
# Pre-requisites: 
# - Sign in to the Azure CLI ("az login") and set the subscription ("az account set --subscription <subscription>").
# - Install the network-analytics Azure CLI extension: "az extension add --name network-analytics"
# - Install the AzCopy tool and add the executable to your system path: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10 

set -euo pipefail
export AZCOPY_AUTO_LOGIN_TYPE=AZCLI

# Set variables for resource group, Data Product name, data type, and the URL of the files in the source
# Storage Account (including container and directory).
# Replace these values with your own.
resourceGroup="myResourceGroup"
dataProductName="myDataProduct"
dataType="myDataType"
sourceDataUrl="https://mysourceaccount.blob.core.windows.net/myContainer/myBlobDirectory"

# Call the script that sets environment variables for the ingestion parameters.
source ../snippets/az-cli-set-ingestion-params.sh "$resourceGroup" "$dataProductName"

# Copy the files from the source Storage Account to the ingestion URL using AzCopy.
# This copies all files in $sourceDataUrl. See https://learn.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-copy
# for more options, including filtering.
# This fails if the identity used to run the script does not have permissions to read from the source Storage Account.
destination_path="testdata/date-$(date +%d-%m-%Y)"
echo "Copying files from Azure Storage $sourceDataUrl to $INGESTION_URL/$dataType/$destination_path"
azcopy copy "$sourceDataUrl" "$INGESTION_URL/$dataType/$destination_path?$INGESTION_SAS_TOKEN" --recursive=true
