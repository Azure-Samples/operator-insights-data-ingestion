# Ingestion using Azure Databricks

## When to use Azure Databricks to ingest in to Azure Operator Insights

Azure Databricks provides a convenient solution for ingesting from a variety of data sources directly in to an [Azure Operator Insights data product](https://learn.microsoft.com/en-us/azure/operator-insights/).

Using Databricks is recommended if:

- The data source is supported by Azure Databricks
  - For information about connecting to other supported data sources, see [Azure Databricks documentation/Connect to data sources (MS Learn)](https://learn.microsoft.com/en-us/azure/databricks/connect/)
- You require continuous ingestion
- The data you would like to ingest contains a transaction log (E.g. Delta file format)
  - In this scenario, your databricks ingestion workflow can convert to a file format that Azure Operator Insights supports
- You wish to apply transformations or filtering to your data before it is ingested to your data product

### Authentication to Azure Operator Insights

**Azure Databricks does not currently support reading the SAS URL directly from the Data Product's Key Vault.** This is because the Data Product's Key Vault uses the Role-Based Access Control (RBAC) Permission model, which is unsupported by Azure Databricks

The recommended approach of providing the SAS URL (and other secrets) to Azure Databricks is to _use an Azure Key Vault-backed secret scope with a Key Vault that has the 'Access policy' Permission model._

[Create an Azure Key Vault-backed secret scope (MS Learn)](https://learn.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes#--create-an-azure-key-vault-backed-secret-scope) describes how to do this

After the secret scope is created, _copy the SAS URL from the Data Product's Key Vault to the Databricks 'Access Policy' keyvault_ such that it's value can be accessed from a Databricks job. Any other secrets required by the job can also be stored and accessed from the same Key Vault.

#### How to Copy the ingestion SAS URL to the 'Access Policy' key vault

  1. Find the resource group which contains the managed Key Vault for the data product. This Key Vault contains the SAS URL for ingesting files in to Azure Operator Insights.
      - The resource group has a naming convention of `<data-product-name>-HostedResources-<unique-hex-string>`
      - This can be found in the azure portal by searching for your data product name
  1. Open the managed key vault within the resource group and navigate to the `Secrets` tab
      - The key vault has a naming convention of `aoi-dp<unique-id>-kv`
  1. Find the secret named `input-storage-sas`
      - You will need at least the `Key Vault Secrets User` role on the Key Vault to view the value of the secret
  1. Create a new secret in the *Access policy Key Vault*, created in the previous steps
  1. Copy the value of the `input-storage-sas` secret in the managed key vault to the new secret in the *Access policy Key Vault*. Click the `Create` button to save the new secret

> **Important**: The SAS URL will not be automatically updated in the *'Access policy' Key Vault_ when it is rotated. This will cause your Databricks ingestion job to fail when the initial SAS URL expires. The default expiry time for ingestion SAS URLs is 3 months.
To avoid this, **the new SAS URL must be uploaded to the _'Access policy Key Vault'_ when it is rotated**.

## Ingestion sample notebook

To get started, a [sample ingestion notebook](databricks-aoi-ingestion.py) is provided. See also [DATABRICKS-SAMPLE.md](./DATABRICKS-SAMPLE.md) for details on the environment in which the notebook's job is expected to run.
