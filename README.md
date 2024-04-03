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
- An Azure Entra identity to use to run the sample. The identity must have the following roles:
  - _Reader_ role on your data product
  - _Key Vault Secrets User_ role on the managed key vault associated with your data product.

Additional sample-specific prerequisites are listed in the code or README files for each sample.

### Quickstart

1. `git clone https://github.com/Azure-Samples/operator-insights-data-ingestion.git`
2. `cd operator-insights-data-ingestion/samples`
3. Choose a sample, update the required parameters to work with your data product and data source, and run the sample.

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

- To ingest EDRs from an Affirmed MCC, or to ingest files from an SFTP server, you can use the [Azure Operator Insights Ingestion Agent](https://learn.microsoft.com/en-us/azure/operator-insights/ingestion-agent-overview).
