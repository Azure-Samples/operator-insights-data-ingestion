#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is an example bash script that demonstrates how to upload data from a local directory to an 
# Azure Operator Insights data product using the Azure CLI and the AzCopy tool.
# To use the script, fill in the variables at the top of the script and run it from the command line.
# 
# Pre-requisites: 
# - Log in to the Azure CLI ("az login") and set the subscription ("az account set --subscription <subscription>").
# - Install the network-analytics Azure CLI extension: "az extension add --name network-analytics"
# - Install the AzCopy tool and add the executable to your system path: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10 

set -euo pipefail

# Set variables for resource group, data product name, data type, and the local filepath of the files to upload.
# Replace these values with your own.
resourceGroup="myResourceGroup"
dataProductName="myDataProduct"
dataType="myDataType"
sourceDataFilePath="path/to/local/dir"

# Call the script that sets environment variables for the ingestion parameters.
source ../snippets/az-cli-set-ingestion-params.sh "$resourceGroup" "$dataProductName"

# Copy the files in sourceDataFilePath to the ingestion URL using AzCopy.
# This copies all files in $sourceDataFilePath. See https://learn.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-copy
# for more options, including filtering.
destination_path="testdata/date-$(date +%d-%m-%Y)"
echo "Uploading files from local path $sourceDataFilePath to $INGESTION_URL/$dataType/$destination_path"
azcopy copy "$sourceDataFilePath" "$INGESTION_URL/$dataType/$destination_path?$INGESTION_SAS_TOKEN" --recursive=true
