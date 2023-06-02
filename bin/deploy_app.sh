#!/bin/bash

# sed all SED_* variables to replace deploy_containerapp.yaml, such as 
# SED_INPUT_STORAGE_ACCOUNT, SED_INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING, SED_INPUT_STORAGE_CONTAINER, SED_OUTPUT_STORAGE_ACCOUNT, SED_OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING, SED_OUTPUT_STORAGE_CONTAINER

input_storage_connectionstring=$(az storage account show-connection-string --name ${INPUT_STORAGE_ACCOUNT} --resource-group ${INPUT_RESOURCE_GROUP} --query connectionString)
output_storage_connectionstring=$(az storage account show-connection-string --name ${OUTPUT_STORAGE_ACCOUNT} --resource-group ${OUTPUT_RESOURCE_GROUP} --query connectionString)
managed_environment_id=$(az containerapp env show --name $CONTAINERAPP_ENVIRONMENT -g ${APP_RESOURCE_GROUP} --query id)

az containerapp create --name $CONTAINERAPP_NAME --resource-group $APP_RESOURCE_GROUP \
    --environment $CONTAINERAPP_ENVIRONMENT \
    --image $IMAGE_URL \
    --env-vars "INPUT_STORAGE_ACCOUNT=$INPUT_STORAGE_ACCOUNT" \
        "INPUT_STORAGE_CONTAINER=$INPUT_STORAGE_CONTAINER" \
        "INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING=$input_storage_connectionstring" \
        "OUTPUT_STORAGE_ACCOUNT=$OUTPUT_STORAGE_ACCOUNT" \
        "OUTPUT_STORAGE_CONTAINER=$OUTPUT_STORAGE_CONTAINER" \
        "OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING=$output_storage_connectionstring"

# replace SED_AZURE_FILE_SHARE_NAME_MOUNT in deploy_containerapp_template.yaml
sed "s#SED_AZURE_FILE_SHARE_NAME_MOUNT#$AZURE_FILE_SHARE_NAME_MOUNT#g" bin/deploy_containerapp_template.yaml > bin/deploy_containerapp.yaml
sed -i "s#SED_IMAGE_URL#$IMAGE_URL#g" bin/deploy_containerapp.yaml

az containerapp update --name $CONTAINERAPP_NAME --resource-group $APP_RESOURCE_GROUP --yaml bin/deploy_containerapp.yaml

az containerapp update --name $CONTAINERAPP_NAME --resource-group $APP_RESOURCE_GROUP \
    --set-env-vars "INPUT_STORAGE_ACCOUNT=$INPUT_STORAGE_ACCOUNT" \
        "INPUT_STORAGE_CONTAINER=$INPUT_STORAGE_CONTAINER" \
        "INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING=$input_storage_connectionstring" \
        "OUTPUT_STORAGE_ACCOUNT=$OUTPUT_STORAGE_ACCOUNT" \
        "OUTPUT_STORAGE_CONTAINER=$OUTPUT_STORAGE_CONTAINER" \
        "OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING=$output_storage_connectionstring"

az containerapp udpate --name $CONTAINERAPP_NAME --resource-group $APP_RESOURCE_GROUP \
    --image tomqwu/dicom-etl-dapr:0.1.24