# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# This is an example Python script that demonstrates how to upload data to an Azure Operator Insights
# Data Product using the Azure SDK.
# https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-overview
# To use the script, fill in the variables at the top of the script and run it from the command line.
# e.g `python3.9 python-aoi-ingestion.py`
#
# The script uses the Azure credentials of the user running the script to authenticate with Azure services. This auth method is
# suitable for prototyping: see https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication-overview?view=azure-python
# for information about other methods of authenticating with Azure services which are more appropriate for production use.
#
# Pre-requisites:
# - Install a supported version of Python, at least 3.9: https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy
# - Install the required Azure SDK libraries ("pip install azure-storage-blob azure-identity azure-keyvault-secrets azure-mgmt-networkanalytics")
# - Sign in to the Azure CLI ("az login").
# - Set the AZURE_SUBSCRIPTION_ID environment variable to your Azure subscription ID.

import os
import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from azure.mgmt.networkanalytics import NetworkAnalyticsMgmtClient


def main():
    # Set variables for resource group, Data Product name, data type, and the local filepath of the files to upload.
    # Replace these values with your own.
    resource_group = "myResourceGroup"
    data_product_name = "myDataProduct"
    data_type = "myDataType"
    source_data_file_path = "path/to/local/dir"

    # Fetch the subscription ID from the environment variables.
    sub_id = os.environ["AZURE_SUBSCRIPTION_ID"]

    # Use the Network Analytics client library to get the ingestion URL.
    credential = DefaultAzureCredential()
    client = NetworkAnalyticsMgmtClient(credential=credential, subscription_id=sub_id)
    ingestion_url = client.data_products.get(
        resource_group, data_product_name
    ).properties.consumption_endpoints.ingestion_url

    # Break out the Data Product ID from the ingestion URL.
    # If the ingestion URL is "https://aoiingestiondp123abc.blob.core.windows.net", then the data
    # product ID is "dp123abc".
    data_product_id = ingestion_url.removeprefix("https://aoiingestion").removesuffix(
        ".blob.core.windows.net"
    )

    # Use the Data Product ID to generate the URL of the managed key vault
    key_vault_url = f"https://aoi-{data_product_id}-kv.vault.azure.net/"

    # Fetch the SAS URL from the key vault using the Key Vault Secret client library, and extract the
    # SAS token from the URL. The SAS token is everything after the '?' character.
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
    sas_url = secret_client.get_secret("input-storage-sas").value
    sas_token = sas_url.split("?")[1]

    # Copy the files in source_data_file_path to the ingestion URL using the Azure Storage client library.
    # This example does not preserve the directory structure of the source files.
    blob_service_client = BlobServiceClient(
        account_url=ingestion_url, credential=sas_token
    )
    container_client = blob_service_client.get_container_client(data_type)
    destination_path = f"testdata/date-{datetime.datetime.now().strftime('%d-%m-%Y')}"
    print(f"Uploading files from local path {source_data_file_path} to {ingestion_url}/{data_type}/{destination_path}")

    for root, _, files in os.walk(source_data_file_path):
        for file in files:
            source_file_path = os.path.join(root, file)
            blob_client = container_client.get_blob_client(
                destination_path + "/" + file
            )
            with open(source_file_path, "rb") as data:
                blob_client.upload_blob(data)

    print(f"Files uploaded successfully from local path {source_data_file_path}")

if __name__ == "__main__":
    main()
