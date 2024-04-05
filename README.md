# Azure Operator Insights data ingestion samples

Code samples and guidance demonstrating how to ingest data into an [Azure Operator Insights data product](https://learn.microsoft.com/en-us/azure/operator-insights/).

Azure Operator Insights offers a range of options for ingesting data into data products:

- The [Azure Operator Insights Ingestion Agent](https://learn.microsoft.com/en-us/azure/operator-insights/ingestion-agent-overview), which runs on-prem or on an Azure VM. The agent can consume data from different sources and upload the data to an Azure Operator Insights data product. The agent currently supports ingestion by:
  - Pulling data from an SFTP server
  - Terminating a TCP stream of enhanced data records (EDRs) from the Affirmed MCC.
- Other Azure services and tools. A variety of tools can be used to upload data to an Azure Operator Insights data product. For example:
  - AzCopy is a simple tool for uploading batches of data from a variety of local or cloud storage locations.
  - Azure Data Factory allows you to define more complicated pipelines to process the data before uploading to the data product.  (\<TODO insert Learn link when published>)
- Build your own ingestion, using the code samples in this repository as a starting point.

## Getting Started

Read this README then explore the samples directory: [samples](samples).

### Prerequisites

For all of the samples, you need:

- An Azure Operator Insights Data Product
- A Microsoft Entra identity to use to run the sample. The identity must have the following roles:
  - _Reader_ role on your data product
  - _Key Vault Secrets User_ role on the managed key vault associated with your data product.

Additional sample-specific prerequisites are listed in the code or README files for each sample.

### Quickstart

1. `git clone https://github.com/Azure-Samples/operator-insights-data-ingestion.git`
2. `cd operator-insights-data-ingestion/samples`
3. Choose a sample, update the required parameters to work with your data product and data source, and run the sample.

### Next steps

The samples in this repository demonstrate how to implement basic ingestion into a data product, and they are provided for prototyping and educational purposes only.

Before using these samples as part of a production system, you should consider what additional logging, security, performance and resilience you need to add to make the code suitable for production use.

## Samples

### End-to-end samples

- Azure CLI: [samples/end-to-end/az-cli-aoi-ingestion.sh](samples/end-to-end/az-cli-aoi-ingestion.sh)
- AzCopy:
  - Upload from local directory: [samples/end-to-end/azcopy-aoi-ingestion-from-local.sh](samples/end-to-end/azcopy-aoi-ingestion-from-local.sh)
  - Copy from an Azure Storage Account: [samples/end-to-end/azcopy-aoi-ingestion-from-storage-account.sh](samples/end-to-end/azcopy-aoi-ingestion-from-storage-account.sh)
- Python, using Azure SDK for Python: [samples/end-to-end/python-aoi-ingestion.py](samples/end-to-end/python-aoi-ingestion.py)

All end-to-end samples follow three steps:

1. Find the name of the managed key vault associated with the data product, by querying the data product to find the data product's unique ID
2. Authenticate with the managed key vault and fetch the secret containing the ingestion SAS URL for the data product.
3. Using the ingestion URL/storage account name and ingestion SAS token, upload data to the ingestion endpoint of the data product.

### Sample snippets

- Setup script: Use the Azure CLI to perform steps 1 and 2 above, saving the parameters as environment variables: [samples/snippets/az-cli-set-ingestion-params.sh](samples/snippets/az-cli-set-ingestion-params.sh)


### Common parameters

Most samples require the same parameters:

- `resourceGroup`: the resource group where the data product is deployed
- `dataProductName`: the name of the data product to upload data to
- `dataType`: the data type name for the data to upload, e.g. `edr` or `pmstat`. The valid data types for a data product are listed on the _Data Management > Data types_ pane of the Azure Portal for the data product.
- `sourceDataFilePath`: the path to a local directory containing the files you want to upload to the data product

All samples must authenticate with the managed key vault that is associated with the data product. This authentication is handled differently depending on the sample.



## Resources

- To learn about Azure Operator Insights, visit [Azure Operator Insights documentation](https://learn.microsoft.com/en-us/azure/operator-insights/).
- To ingest EDRs from an Affirmed MCC, or to ingest files from an SFTP server, you can use the [Azure Operator Insights Ingestion Agent](https://learn.microsoft.com/en-us/azure/operator-insights/ingestion-agent-overview).
- For details of the Azure Operator Insights (network-analytics) Azure CLI extension, see [Azure CLI reference: az network-analytics](https://learn.microsoft.com/en-us/cli/azure/network-analytics?view=azure-cli-latest).
- For guidance on using AzCopy to copy files to an Azure Storage Account (including Azure Operator Insights data product ingestion storage), see [Get started with AzCopy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10).
- To learn more about developing your own Azure Operator Insights data product, visit [Azure Operator Insights data product factory](https://learn.microsoft.com/en-us/azure/operator-insights/data-product-factory).
