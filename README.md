# Pathology ETL
## Overview 

```plantuml
@startuml
actor DaprEventQueue
participant "Flask App" as App
participant "Azure Blob Storage" as Azure
participant "Mounted Azure File Share" as Local
participant "WsiDicomizer" as Wsi
participant "Pydicom" as Pyd

DaprEventQueue -> App: Event (with blob file URL)
App -> Azure: Download blob file
Azure --> App: Blob file
App -> Local: Save blob file
App -> Wsi: Convert blob file to DCM
Wsi --> App: DCM files
App -> Pyd: Mutate Patient ID in DCM files
Pyd --> App: DCM files with new Patient ID
App -> Azure: Upload DCM files
Azure --> App: Confirmation
App --> DaprEventQueue: Acknowledge event
@enduml
```

![image](./images/RP3FRi8m3CRlUGgBqtRW1NgO-DCXJGA93Q6TJMiW8asYrA4QJx_429LCExNox_Uv_Zhh6GF7pYXis0MeqOVtArd-Z1H9-GHreprQXidAO7-1kVSJm3u_Ipo_nK2mCEu0kxGAJoIUZ4jpuw9bQky8LjeGxCuOxlxQDMXA_xlNjMvSfsyKn4c3qjZ-j5aGcDwLAdl0z2tVMu6Cu6NGV8P3llIO.png)
## Prerequisites
- Python 3.6+
- Azure CLI
- Azure Storage Account
- Azure Container App


## Setup

```bash
export LOCATION=canadacentral
export INPUT_RESOURCE_GROUP=dicom-rg
export APP_RESOURCE_GROUP=dicom-rg
export OUTPUT_RESOURCE_GROUP=dicom-rg

export INPUT_STORAGE_ACCOUNT=sphdicomviewer
export INPUT_STORAGE_CONTAINER=wsi-input
export OUTPUT_STORAGE_ACCOUNT=sphdicomviewer
export OUTPUT_STORAGE_CONTAINER=dicom-output

export INPUT_WSI_TRIGGER_NAME=incoming-wsi-trigger

export CONTAINERAPP_NAME=wsi-to-dicom
export CONTAINERAPP_ENVIRONMENT=wsi-to-dicom
export IMAGE_URL=tomqwu/dicom-etl-dapr:0.1.20
export AZURE_FILE_SHARE_NAME_MOUNT=wsi-to-dicom
```

```bash
./deploy_infra.sh
./deploy_app.sh
```

## Usage

drop files into input container