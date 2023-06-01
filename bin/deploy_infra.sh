#!/bin/bash

# create storage queue for wsi file trigger
az storage queue create -n ${INPUT_WSI_TRIGGER_NAME} --account-name ${INPUT_STORAGE_ACCOUNT}

# create eventgrid system topic for wsi file trigger
storage_id=$(az storage account show --name ${INPUT_STORAGE_ACCOUNT} -g dicom-rg --query id -o tsv)
az eventgrid system-topic create --name ${INPUT_WSI_TRIGGER_NAME} \
  --location $LOCATION \
  -g ${INPUT_RESOURCE_GROUP} \
  --topic-type microsoft.storage.storageaccounts \
  --source ${storage_id}

# create az eventgrid system-topic event-subscription create for wsi file trigger create blob and end with .ndpi
az eventgrid system-topic event-subscription create --name ${INPUT_WSI_TRIGGER_NAME} \
    --system-topic-name ${INPUT_WSI_TRIGGER_NAME} \
    --resource-group ${INPUT_RESOURCE_GROUP} \
    --endpoint-type storagequeue \
    --included-event-types Microsoft.Storage.BlobCreated \
    --endpoint ${storage_id}/queueservices/default/queues/${INPUT_WSI_TRIGGER_NAME} \
    --subject-begins-with /blobServices/default/containers/${INPUT_STORAGE_CONTAINER}/ \
    --subject-ends-with .ndpi

# create storage file share for container mounting
az storage share create -n ${AZURE_FILE_SHARE_NAME_MOUNT} --account-name ${INPUT_STORAGE_ACCOUNT}

# create container app environment
az containerapp env create \
  --name $CONTAINERAPP_ENVIRONMENT \
  --resource-group $APP_RESOURCE_GROUP \
  --location $LOCATION

input_storage_account_key=$(az storage account keys list -n ${INPUT_STORAGE_ACCOUNT} -g ${APP_RESOURCE_GROUP} -o json --query "[0].value" -o tsv)
az containerapp env storage set \
  --name $CONTAINERAPP_ENVIRONMENT --resource-group $APP_RESOURCE_GROUP \
  --storage-name ${AZURE_FILE_SHARE_NAME_MOUNT} \
  --azure-file-account-name ${INPUT_STORAGE_ACCOUNT} \
  --azure-file-account-key ${input_storage_account_key} \
  --azure-file-share-name ${AZURE_FILE_SHARE_NAME_MOUNT} \
  --access-mode ReadWrite

sed "s/SED_INPUT_STORAGE_ACCOUNT/$INPUT_STORAGE_ACCOUNT/g" bin/input_storage_queue_template.yaml > bin/input_storage_queue.yaml
sed -i "s/SED_INPUT_STORAGE_QUEUE/$INPUT_WSI_TRIGGER_NAME/g" bin/input_storage_queue.yaml
sed -i "s/SED_STORAGE_ACCOUNT_ACCESS_KEY/$input_storage_account_key/g" bin/input_storage_queue.yaml

az containerapp env dapr-component set \
    --name $CONTAINERAPP_ENVIRONMENT  --resource-group $APP_RESOURCE_GROUP \
    --dapr-component-name queueinput \
    --yaml bin/input_storage_queue.yaml
