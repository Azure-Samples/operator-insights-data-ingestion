# Overview

The sample notebook is used to create a Databricks job that reads Delta files from an Azure Storage Account container, filters and transforms them to CSV, and ingests them in to Azure Operator Insights.

## How to use the sample notebook

[The sample ingestion notebook](./databricks-aoi-ingestion.py) is a reference to be used along side the [Azure Databricks documentation (MS Learn)](https://learn.microsoft.com/en-us/azure/databricks/) to create an ingestion solution which fits your requirements.

Details of the environment in which the sample notebook is intended to run are provided below

## Diagram

TODO: Add a diagram

## Environment

- Data to be ingested exists in [Delta format](https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/delta-lake) in an Azure Storage Account container
- A separate Storage Account exists in the same subscription, in which the following files are written by the Databricks workflow:
  - Delta checkpoint files, which are required for Databricks to correctly process Delta. _This will not be required if the Delta file format is not used_
  - [Files which contain bad records](https://learn.microsoft.com/en-us/azure/databricks/ingestion/bad-records)

- A Service Principal exists which is used to authenticate to the storage accounts. It has the following RBAC roles:
  - _Storage Blob Data Reader_ on the Storage Account which contains the source delta files
  - _Storage Blob Data Contributor_ on the Storage Account where checkpoint and bad records files are written
- The example notebook is run as a [continuous job](https://learn.microsoft.com/en-us/azure/databricks/workflows/jobs/schedule-jobs#--run-a-continuous-job)
- An Azure Key Vault-backed secret scope exists in Azure Databricks which points to a Key Vault with the 'Access Policy' Permission model, as described in the [Authentication to Azure Operator Insights](./README.md#authentication-to-azure-operator-insights) section
- The following secrets exist in the aforementioned Key Vault:
  - Data product ingestion SAS URL
  - The Service Principal's Application (client) ID
  - The Service Principal's Directory (tenant) ID
  - The Service Principal's Client Secret value
