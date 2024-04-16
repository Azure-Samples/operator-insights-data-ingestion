#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is an example bash script that demonstrates how to upload data to an Azure Operator Insights 
# Data Product using the Azure CLI.
# To use the script, fill in the variables at the top of the script and run it from the command line.
#
# Pre-requisites: 
# - Sign in to the Azure CLI ("az login") and set the subscription ("az account set --subscription <subscription>").
# - Install the network-analytics Azure CLI extension: "az extension add --name network-analytics".

set -euo pipefail

# Set variables for resource group, Data Product name, data type, and the local filepath of the files to upload.
# Replace these values with your own.
resourceGroup="myResourceGroup"
dataProductName="myDataProduct"
dataType="myDataType"
sourceDataFilePath="path/to/local/dir"

# Call the script that sets environment variables for the ingestion parameters.
source ../snippets/az-cli-set-ingestion-params.sh "$resourceGroup" "$dataProductName"

# Copy the files in sourceDataFilePath to the ingestion URL using az storage CLI command
# This copies all files in $sourceDataFilePath. See https://learn.microsoft.com/en-us/cli/azure/storage/blob?view=azure-cli-latest#az-storage-blob-upload-batch 
# for more options, including filtering.
destination_path="testdata/date-$(date +%d-%m-%Y)"
echo "Uploading files from local path $sourceDataFilePath to $INGESTION_URL/$dataType/$destination_path"
az storage blob upload-batch --blob-endpoint "$INGESTION_URL" --source "$sourceDataFilePath" --destination "$dataType" --destination-path "$destination_path" --sas-token "$INGESTION_SAS_TOKEN" --output none
