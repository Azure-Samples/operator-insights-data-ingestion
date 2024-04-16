# Azure Operator Insights data ingestion samples

Code samples and guidance demonstrating how to ingest data into an [Azure Operator Insights Data Product](https://learn.microsoft.com/en-us/azure/operator-insights/).

Azure Operator Insights offers a range of options for ingesting data into Data Products:

- The [Azure Operator Insights ingestion agent](https://learn.microsoft.com/en-us/azure/operator-insights/ingestion-agent-overview), which runs on-premises or on an Azure VM. The agent can consume data from different sources and upload the data to an Azure Operator Insights Data Product. The agent currently supports ingestion by:
  - Pulling data from an SFTP server
  - Terminating a TCP stream of enhanced data records (EDRs) from the Affirmed MCC.
- Ingestion via other methods:
  - Existing Microsoft or third-party tools which upload data to Azure. E.g. [AzCopy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10) or [Azure Data Factory](https://learn.microsoft.com/en-us/azure/operator-insights/ingestion-with-data-factory).
  - Custom code, e.g. using the Azure CLI or Azure SDK.

The Azure Operator Insights ingestion agent is the recommended ingestion method for the use cases it supports.

For other use cases, this repository provides samples of ingestion using common Microsoft tools or custom code.

## Getting Started

Read this README then explore the samples directory: [samples](samples). When you want more in-depth guidance on implementing ingestion, read [INGESTION-OVERVIEW.md](INGESTION-OVERVIEW.md).

### Prerequisites

For most of the samples, you need:

- An Azure Operator Insights Data Product
- A Microsoft Entra identity to use to run the sample. The identity must have the following roles:
  - _Reader_ role on your Data Product
  - _Key Vault Secrets User_ role on the managed key vault associated with your Data Product.

Some samples have different prerequisites, which are listed in the code or README files for each sample (e.g. for [Azure Databricks](samples/end-to-end/azure-databricks/README.md)).

### Quickstart

1. `git clone https://github.com/Azure-Samples/operator-insights-data-ingestion.git`
2. `cd operator-insights-data-ingestion/samples`
3. Choose a sample, update the required parameters to work with your Data Product and data source, and run the sample.

### Next steps

The samples in this repository demonstrate how to implement basic ingestion into a Data Product, and they are provided for prototyping and educational purposes only.

Before using these samples as part of a production system, you should consider what additional logging, security, performance and resilience you need to add to make the code suitable for production use.

## Samples

### End-to-end samples

- [Azure CLI](samples/end-to-end/az-cli-aoi-ingestion.sh)
- AzCopy:
  - [Upload from local directory](samples/end-to-end/azcopy-aoi-ingestion-from-local.sh)
  - [Copy from an Azure Storage Account](samples/end-to-end/azcopy-aoi-ingestion-from-storage-account.sh)
- [Python](samples/end-to-end/python-aoi-ingestion.py), using Azure SDK for Python
- [Azure Databricks](samples/end-to-end/azure-databricks/README.md)

Most end-to-end samples follow three steps:

1. Find the name of the managed key vault associated with the Data Product, by querying the Data Product to find the Data Product's unique ID
2. Authenticate with the managed key vault and fetch the secret containing the ingestion SAS URL for the Data Product.
3. Using the ingestion URL/storage account name and ingestion SAS token, upload data to the ingestion endpoint of the Data Product.

### Helper code snippets

- Setup script: Use the Azure CLI to perform steps 1 and 2 above, saving the parameters as environment variables: [samples/snippets/az-cli-set-ingestion-params.sh](samples/snippets/az-cli-set-ingestion-params.sh)

### Common parameters

Most samples require the same parameters:

- `resourceGroup`: the resource group where the Data Product is deployed
- `dataProductName`: the name of the Data Product to upload data to
- `dataType`: the data type name for the data to upload, e.g. `edr` or `pmstat`. The valid data types for a Data Product are listed on the _Data Management > Data types_ pane of the Azure Portal for the Data Product.
- `sourceDataFilePath`: the path to a local directory containing the files you want to upload to the Data Product

All samples must authenticate with the managed key vault that is associated with the Data Product. This authentication is handled differently depending on the sample.

## Resources

- To learn about Azure Operator Insights, visit [Azure Operator Insights documentation](https://learn.microsoft.com/en-us/azure/operator-insights/).
- To ingest EDRs from an Affirmed MCC, or to ingest files from an SFTP server, you can use the [Azure Operator Insights Ingestion Agent](https://learn.microsoft.com/en-us/azure/operator-insights/ingestion-agent-overview).
- For details of the Azure Operator Insights (network-analytics) Azure CLI extension, see [Azure CLI reference: az network-analytics](https://learn.microsoft.com/en-us/cli/azure/network-analytics?view=azure-cli-latest).
- For guidance on using AzCopy to copy files to an Azure Storage Account (including Azure Operator Insights Data Product ingestion storage), see [Get started with AzCopy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10).
- To learn more about developing your own Azure Operator Insights Data Product, visit [Azure Operator Insights Data Product factory](https://learn.microsoft.com/en-us/azure/operator-insights/data-product-factory).
