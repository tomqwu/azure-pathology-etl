#!/bin/bash

export RESOURCE_GROUP=pathology-poc
export LOCATION=canadacentral
export CONTAINERAPPS_ENVIRONMENT=pathology-poc
export CONTAINERAPP_NAME=dicom-etl

az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION"

az containerapp env storage set \
  --name $CONTAINERAPPS_ENVIRONMENT --resource-group $RESOURCE_GROUP \
  --storage-name dicom-etl \
  --azure-file-account-name ndpi \
  --azure-file-account-key Gzv/NVzQeJfd0jLl6vmwXRl1WrZ96Eynbg+jnCq4VRE8XWws1XNGX7tx+dAvhmUV3lbg7cFKuzb4+ASt4owGkQ== \
  --azure-file-share-name dicom-etl \
  --access-mode ReadWrite

az containerapp env dapr-component set \
    --name $CONTAINERAPPS_ENVIRONMENT  --resource-group $RESOURCE_GROUP \
    --dapr-component-name queueinput \
    --yaml input_storage_queue.yaml
