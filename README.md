# Pathology ETL
## Overview 


## Prerequisites
- Python 3.6+
- Azure CLI
- Azure Storage Account
- Azure Container Registry
- Azure Container App


## Setup

```bash
export RESOURCE_GROUP=pathology-poc
export CONTAINERAPP_NAME=dicom-etl
export INPUT_STORAGE_ACCOUNT=ndpi
export INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING=CONNECTION_STRING_REPLACE
export INPUT_STORAGE_CONTAINER=input
export OUTPUT_STORAGE_ACCOUNT=dcmoutput
export OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING=CONNECTION_STRING_REPLACE
export OUTPUT_STORAGE_CONTAINER=output
```


`./deploy_infra.sh`

`./deploy_app.sh`

## Usage

drop files into input container