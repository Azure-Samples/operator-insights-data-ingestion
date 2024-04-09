# Databricks notebook source
# Copyright (C) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.md in the project root for license information.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read Source files in Delta format available at customer storage location and load into AOI input storage
# MAGIC

# COMMAND ----------

# DBTITLE 1,Import common packages
import os
import logging
from datetime import datetime, timedelta

from pyspark.sql import DataFrame
from pyspark.dbutils import DBUtils
import pyspark.sql.functions as F

# COMMAND ----------

# DBTITLE 1,Set up Common Spark Configuration
# This is to store state data
dbutils = DBUtils(spark)
spark.conf.set(
    "spark.sql.streaming.stateStore.providerClass",
    "com.databricks.sql.streaming.state.RocksDBStateStoreProvider",
)
spark.conf.set("spark.sql.files.ignoreMissingFiles", True)
spark.conf.set("spark.sql.files.ignoreCorruptFiles", False)
spark.conf.set("spark.sql.streaming.noDataMicroBatches.enabled", False)

# COMMAND ----------

# DBTITLE 1,Set up Common Environment Context Variables and logger
notebook_name = (
    dbutils.notebook.entry_point.getDbutils()
    .notebook()
    .getContext()
    .notebookPath()
    .get()
)

job_name = os.path.basename(notebook_name)
logger = logging.getLogger("databricks_aoi_ingestion")
logger.setLevel(logging.INFO)  # Default is WARN.
logging.basicConfig(level=logging.INFO)
logger.info("Job started")

# COMMAND ----------



# MAGIC %md
# MAGIC For simplicity, the variables in the following section are hard coded here. The recommended long term approach is to pass parameters to the Databricks job task
# MAGIC using the method described in [Pass parameters to an Azure Databricks job task (MS Learn)](https://learn.microsoft.com/en-us/azure/databricks/workflows/jobs/create-run-jobs#--pass-parameters-to-an-azure-databricks-job-task)
# MAGIC

# COMMAND ----------

# DBTITLE 1, Define variables

# The name of the storage account which contains source files
SOURCE_STORAGE_ACCOUNT_NAME = "source-storage-account"
# The name of the container in the storage account which contains source files
SOURCE_CONTAINER_NAME = "source-container"
# The file path in the container which contains the source files
SOURCE_FILE_PATH = "source/file/path/example"
# The name of the storage account where checkpoint and bad records files will be written
CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME = "checkpoint-bad-records-storage-account"
# The name of the container in the storage account where bad records files will be written
BAD_RECORDS_CONTAINER_NAME = "bad-records-container"
# The file path in the container where bad records files will be written
BAD_RECORDS_FILE_PATH = "bad_records/file/path/example"
# The name of the container in the storage account where checkpoint files will be written
CHECKPOINT_CONTAINER_NAME = "checkpoint-container"
# The file path in the container where checkpoint files will be written
CHECKPOINT_FILE_PATH = "checkpoint/file/path/example"
# The name of the Azure storage account within the Data Product where the data will be uploaded to for processing by Azure Operator Insights. This can be
# found as part of the SAS URL in the form: https://<AOI_INGESTION_STORAGE_ACCOUNT_NAME>.blob.core.windows.net/?sv=...
AOI_INGESTION_STORAGE_ACCOUNT_NAME = "aoiingestiondp000000"
# The container within the Azure Operator Insights where files will be uploaded. This must be set to exactly as specified in your Data Product's documentation
AOI_INGESTION_CONTAINER_NAME = "ingestion-container-name"
# The top level folder within the ingestion container where files will be uploaded. This must be set to exactly as specified in your Data Product's documentation
AOI_INGESTION_TOP_LEVEL_FOLDER = "ingestion-top-level-folder"
# The name of the Azure Key Vault-backed secret scope created in the Azure Databricks workspace
SECRET_SCOPE_NAME = "secret_scope_name"
# The name of the secret in the 'Access Policy' Key Vault which contains the value of the ingestion SAS URL
SECRET_NAME_SAS_URL = "input-storage-sas"
# The name of the secret in the 'Access Policy' Key Vault which contains the value of the service principal's Application (client) ID
SECRET_NAME_CLIENT_ID = "sp-client-id"
# The name of the secret in the 'Access Policy' Key Vault which contains the value of the service principal's Directory (tenant) ID
SECRET_NAME_TENANT_ID = "sp-tenant-id"
# The name of the secret in the 'Access Policy' Key Vault which contains the value of the service principal's secret
SECRET_NAME_CLIENT_SECRET = "sp-client-secret"

# COMMAND ----------

# DBTITLE 1,Set up storage account access by fetching secrets from Azure Key Vault
# Use a service principal to access the source blob storage account, from which we will read the data in delta format, and the checkpoint/bad records storage account.
source_sp_client_id = dbutils.secrets.get(SECRET_SCOPE_NAME, SECRET_NAME_CLIENT_ID)
source_sp_secret = dbutils.secrets.get(SECRET_SCOPE_NAME, SECRET_NAME_CLIENT_SECRET)
source_sp_tenant_id = dbutils.secrets.get(SECRET_SCOPE_NAME, SECRET_NAME_TENANT_ID)
input_auth_endpoint = f"https://login.microsoftonline.com/{source_sp_tenant_id}/oauth2/token"
# Use SAS token to access the AOI input storage account, where we write out the output files.
# The AOI DP key vault provides a full SAS URL, in format “https://<account_name>.blob.core.windows.net?<sas_token>”. Extract the SAS token for use in authentication.
aoi_ingestion_sas_url = dbutils.secrets.get(SECRET_SCOPE_NAME, SECRET_NAME_SAS_URL)
aoi_ingestion_sas_token = aoi_ingestion_sas_url.split("?")[1]

# COMMAND ----------

# MAGIC %md
# MAGIC In this example, the following authentication methods are used:
# MAGIC - The source and checkpoint/bad records storage accounts use OAuth authentication with a service principal which has RBAC permissions on the storage accounts.
# MAGIC     - The source authentication method will depend on where your source files are being ingested from. See [Authentication for Azure Databricks automation - overview (MS Learn)](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/).
# MAGIC - The Azure Operator Insights ingestion storage account (which is the output storage account in this workflow), from which files are processed by the Data Product, uses a SAS token for authentication.
# MAGIC     - This is the recommended approach of authenticating Databricks with Azure Operator Insights.
# MAGIC

# COMMAND ----------

# DBTITLE 1, Configure authentication to storage accounts

# Authentication for the source storage account (service principal & OAuth).
spark.conf.set(
    f"fs.azure.account.auth.type.{SOURCE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    "OAuth",
)
spark.conf.set(
    f"fs.azure.account.oauth.provider.type.{SOURCE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.id.{SOURCE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    source_sp_client_id,
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.secret.{SOURCE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    source_sp_secret,
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.endpoint.{SOURCE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    input_auth_endpoint,
)

# Auth for the Checkpoint and Bad Records storage account (service principal & OAuth).
spark.conf.set(
    f"fs.azure.account.auth.type.{CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    "OAuth",
)
spark.conf.set(
    f"fs.azure.account.oauth.provider.type.{CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.id.{CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    source_sp_client_id,
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.secret.{CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    source_sp_secret,
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.endpoint.{CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    input_auth_endpoint,
)

# Auth for the output storage account (SAS token).
spark.conf.set(
    f"fs.azure.account.auth.type.{AOI_INGESTION_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    "SAS",
)
spark.conf.set(
    f"fs.azure.sas.token.provider.type.{AOI_INGESTION_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.sas.FixedSASTokenProvider",
)
spark.conf.set(
    f"fs.azure.sas.fixed.token.{AOI_INGESTION_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    aoi_ingestion_sas_token,
)

# COMMAND ----------

# DBTITLE 1,Prepare storage account file paths

source_storage_path = f"abfss://{SOURCE_CONTAINER_NAME}@{SOURCE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/{SOURCE_FILE_PATH}"
bad_records_storage_path = f"abfss://{BAD_RECORDS_CONTAINER_NAME}@{CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/{BAD_RECORDS_FILE_PATH}"
checkpoint_storage_path = f"abfss://{CHECKPOINT_CONTAINER_NAME}@{CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/{CHECKPOINT_FILE_PATH}"

# Set up output file path
aoi_ingestion_storage_path = f"abfss://{AOI_INGESTION_CONTAINER_NAME}@{AOI_INGESTION_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/{AOI_INGESTION_TOP_LEVEL_FOLDER}"

logger.info(
    f"""
Source Storage Account Name - {SOURCE_STORAGE_ACCOUNT_NAME}\n
Source Storage Container Name -{SOURCE_CONTAINER_NAME}\n
Source Top level Folder Name - {SOURCE_FILE_PATH}\n
Checkpoint and Bad Records Storage Account Name - {CHECKPOINT_AND_BAD_RECORDS_STORAGE_ACCOUNT_NAME}\n
Bad Records Container Name - {BAD_RECORDS_CONTAINER_NAME}\n
Bad Records folder Path - {BAD_RECORDS_FILE_PATH}\n
Bad Records Path - {bad_records_storage_path}\n
Checkpoint Container Name - {CHECKPOINT_CONTAINER_NAME}\n
Checkpoint folder path - {CHECKPOINT_FILE_PATH}\n
Delta Checkpoint Location - {checkpoint_storage_path}\n
Source Storage Input Path - {source_storage_path}\n
AOI Storage Output Path - {aoi_ingestion_storage_path}\n
"""
)

# COMMAND ----------

# DBTITLE 1,Set up stream reader options
generic_options = {
    # Only required for reading Delta
    "ignoreDeletes": True,
    # Only required for reading Delta
    "maxFilesPerTrigger": 10,
    # Only required for reading Delta
    "maxBytesPerTrigger": 10000000000,
    "mode": "PERMISSIVE",
    "badRecordsPath": bad_records_storage_path,
}

# COMMAND ----------

# MAGIC %md
# MAGIC The next section is where the DataFrame is created. Any filtering or transformation operations on the data should be done in this section after the DataFrame is created.
# MAGIC In this example, two operations are being performed on the data frame:
# MAGIC - The source data contains an 'epoch_timestamp' column which contains the timestamp that an event occurred. In order to avoid ingesting all files in the designated storage account folder, we filter out any records older than 15 minutes
# MAGIC - The source data contains an 'operation_successful' column. We select only records where the value of this field is 'yes'
# MAGIC
# MAGIC Some other useful operations may be:
# MAGIC - Selecting only certain columns
# MAGIC - Adding additional columns which are functions of existing columns
# MAGIC - Adding watermarking, to allow for the arrival of late data
# MAGIC - Dropping duplicate rows
# MAGIC
# MAGIC For an introduction to filtering and transforming data in DataFrames, see [Tutorial: Load and transform data in PySpark DataFrames](https://learn.microsoft.com/en-us/azure/databricks/getting-started/dataframes-python).
# MAGIC For a comprehensive list of operations that can be performed on a DataFrame, see [DataFrame (Spark SQL API documentation)](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/dataframe.html).

# COMMAND ----------

# DBTITLE 1,Create streaming DataFrame and apply any filtering or transformation required
reader_df: DataFrame = (
    spark.readStream.format("delta").options(**generic_options).load(source_storage_path)
)

# Configure the time to start processing files, defined as current time minus 15 minutes
init_time = datetime.now() - timedelta(minutes=15)
processing_start_epoch_time = int(init_time.timestamp())

# filter the DataFrame to select only records where 'operation_successful' is 'yes' and 'epoch_timestamp' is greater than or equal to current time minus 15 minutes
reader_df = reader_df.where(
    ("yes" == F.col("operation_successful"))
    & (F.col("epoch_timestamp") >= processing_start_epoch_time)
).withColumn("file_path", F.input_file_name())

# COMMAND ----------

# DBTITLE 1,Start Reader in Always-On Mode
logger.info(
    f"Start of ingestion block in {notebook_name} notebook"
)

logger.info(f"Writing out to {aoi_ingestion_storage_path}")

# Set the max number of records per file. If you know the size of a single record this will allow you to define the size of the output files.
# CSV files should be no more than 200MiB
spark.conf.set("spark.sql.files.maxRecordsPerFile", 419400)
stream_query_object = (
    reader_df.writeStream.queryName("databricks_aoi_ingestion")
    # Set the output file format. Must be an appropriate file format for your Data Product
    .format("csv")
    .outputMode("append")
    .option("mergeSchema", True)
    .trigger(processingTime="10 seconds")
    .option("checkpointLocation", checkpoint_storage_path)
    .start(aoi_ingestion_storage_path)
)

logger.info(stream_query_object.recentProgress)
