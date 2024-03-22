# How to ingest data into an Azure Operator Insights data product

_If this content belongs better in Learn, just link out to Learn and leave this repo for actual code samples._ 

Add a diagram of the important parts involved in ingestion into a data product.

Then explain the vital steps, to allow people to effectively implement them themselves.

1. Determine where the data is coming from, and how they'll read it from there. Including auth with the data source.
2. Obtain the important info, either by querying Azure resources or feeding it in as config
   1. Data product ingestion endpoint
   2. SAS token/URL (or location and auth to the managed key vault to fetch it from)
   3. Container to upload to. This is generally the data type name
   4. File path to upload to. Free choice, but (for now) must have at least two leading segments (which will be discarded). File paths are mirrored in the data product output storage.
3. Handle rotation of the SAS URL. The samples here do that by fetching the URL every time they run, but ingestion methods that run continuously will want to do something to proactively update.
4. Optional: Implement retry behaviour in case of transient upload issues.