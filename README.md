# Azure Operator Insights data ingestion samples

Code samples and guidance demonstrating how to ingest data into an [Azure Operator Insights data product](https://learn.microsoft.com/en-us/azure/operator-insights/).

## Getting Started

Read this README then explore the samples directory: [samples](samples).

### Prerequisites

For all of the samples, you need:

- TODO
- An Azure Entra identity to use to run the sample. The identity must have at least the _Key Vault Secrets User_ role on the managed key vault associated with your data product.

Sample-specific prerequisites are listed in the code or README files for each sample.

### Quickstart

1. `git clone https://github.com/Azure-Samples/operator-insights-data-ingestion.git`
2. `cd operator-insights-data-ingestion/samples`
3. Choose a sample, add the required parameters to work with your data product and data source, and run the sample.


## Samples

The available samples are:

- Azure CLI: [samples/az-cli-bash-aoi-ingestion.sh](samples/az-cli-aoi-ingestion.sh)
- AzCopy:
  - Upload from local directory: [samples/azcopy-aoi-ingestion-from-local.sh](samples/azcopy-aoi-ingestion-from-local.sh)
  - Copy from an Azure Storage Account: [samples/azcopy-aoi-ingestion-from-storage-account.sh](samples/azcopy-aoi-ingestion-from-storage-account.sh)
- Python, using Azure SDK for Python: [samples/python-aoi-ingestion.py](samples/python-aoi-ingestion.py)

Most samples require the same parameters:

- `rg`: the resource group where the data product is deployed
- `dataProductName`: the name of the data product to upload data to
- `dataType`: the data type name for the data to upload, e.g. `edr` or `pmstat`. The valid data types for a data product are listed on the _Data Management > Data types_ pane of the Azure Portal for the data product.
- `sourceDataFilePath`: the path to a local directory containing the files you want to upload to the data product

In addition, all samples must authenticate with the managed key vault that is associated with the data product. This authentication is handled differently depending on the sample.

All samples follow three steps:

1. Find the name of the managed key vault associated with the data product, by querying the data product to find the data product's unique ID
2. Authenticate with the managed key vault and fetch the secret containing the ingestion SAS URL for the data product.
3. Using the ingestion SAS URL or SAS token, upload data to the ingestion endpoint of the data product.


## Resources

(Any additional resources or related projects)

- TODO
- To ingest EDRs from an Affirmed MCC, or to ingest files from an SFTP server, you can use the [Azure Operator Insights Ingestion Agent](https://learn.microsoft.com/en-us/azure/operator-insights/ingestion-agent-overview).
- ...
