# Pathology ETL
## Overview 

```plantuml
@startuml

actor DaprEventQueue
participant "Flask App" as App
participant "Azure Blob Storage" as Azure
participant "Local Directory" as Local
participant "WsiDicomizer" as Wsi

DaprEventQueue -> App: Event (with blob file URL)
App -> Azure: Download blob file
Azure --> App: Blob file
App -> Local: Save blob file
App -> Wsi: Convert blob file to DCM
Wsi --> App: DCM files
App -> App: Mutate Patient ID in DCM files
App -> Azure: Upload DCM files
Azure --> App: Confirmation
App --> DaprEventQueue: Acknowledge event

@enduml

```

![image](./images/NP1DQiCm48NtEiMGLRl81Rme-L4BXGJQXj3rn9caGsH9oAE4vlIr1e9GLuRtlJV-xCKec2GFpc0l8O75c5wlvEKpKoOJ9yWzH_G2ipU7umMMCSu0n_9iyVAU4y7AXGFi92Gya_OqRfkRqAC3oudAEt-rfbbR-nxPSXy6lbFIpXGOqnh2_AMOTA0HFDrOVk1G74xi2FPVcsSpSQqLaGvik7aN.png)

## Prerequisites
- Python 3.6+
- Azure CLI
- Azure Storage Account
- Azure Container App


## Setup

```bash
export LOCATION=canadacentral
export RESOURCE_GROUP=pathology-poc # assume all resources are in the same resource group
export CONTAINERAPP_NAME=dicom-etl
export AZURE_FILE_SHARE_NAME_MOUNT=dicom-etl
export INPUT_STORAGE_ACCOUNT=ndpi
export INPUT_STORAGE_CONTAINER=input
export OUTPUT_STORAGE_ACCOUNT=dcmoutput
export OUTPUT_STORAGE_CONTAINER=output
export IMAGE_URL=tomqwu/dicom-etl-dapr:0.1.20
```



```bash
./deploy_infra.sh
./deploy_app.sh
```

## Usage

drop files into input container