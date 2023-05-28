#!/bin/bash

az containerapp env create \
  --name $CONTAINERAPP_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION"

input_storage_account_key=$(az storage account keys list -n ${INPUT_STORAGE_ACCOUNT} -g ${RESOURCE_GROUP} -o json --query "[0].value")
az containerapp env storage set \
  --name $CONTAINERAPP_ENVIRONMENT --resource-group $RESOURCE_GROUP \
  --storage-name ${AZURE_FILE_SHARE_NAME_MOUNT} \
  --azure-file-account-name ndpi \
  --azure-file-account-key ${input_storage_account_key} \
  --azure-file-share-name ${AZURE_FILE_SHARE_NAME_MOUNT} \
  --access-mode ReadWrite
  

sed -i "s/SED_STORAGE_ACCOUNT_ACCESS_KEY/$input_storage_account_key/g" input_storage_queue.yaml
az containerapp env dapr-component set \
    --name $CONTAINERAPP_ENVIRONMENT  --resource-group $RESOURCE_GROUP \
    --dapr-component-name queueinput \
    --yaml input_storage_queue.yaml
