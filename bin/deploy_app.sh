#!/bin/bash

# sed all SED_* variables to replace deploy_containerapp.yaml, such as 
# SED_INPUT_STORAGE_ACCOUNT, SED_INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING, SED_INPUT_STORAGE_CONTAINER, SED_OUTPUT_STORAGE_ACCOUNT, SED_OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING, SED_OUTPUT_STORAGE_CONTAINER

input_storage_connectionstring=$(az storage account show-connection-string --name ${INPUT_STORAGE_ACCOUNT} --resource-group ${INPUT_RESOURCE_GROUP} --query connectionString -o tsv)
output_storage_connectionstring=$(az storage account show-connection-string --name ${OUTPUT_STORAGE_ACCOUNT} --resource-group ${OUTPUT_RESOURCE_GROUP} --query connectionString -o tsv)
managed_environment_id=$(az containerapp env show --name ${} -g pathology-poc --query id -o tsv)

deploy_containerapp_template_yaml="bin/deploy_containerapp_template.yaml"

sed -i "s/SED_INPUT_STORAGE_ACCOUNT/$INPUT_STORAGE_ACCOUNT/g" ${deploy_containerapp_template_yaml} > bin/deploy_containerapp.yaml
sed -i "s/SED_INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING/${input_storage_connectionstring}/g" > bin/deploy_containerapp.yaml
sed -i "s/SED_INPUT_STORAGE_CONTAINER/$INPUT_STORAGE_CONTAINER/g" ${deploy_containerapp_template_yaml} > bin/deploy_containerapp.yaml
sed -i "s/SED_OUTPUT_STORAGE_ACCOUNT/$OUTPUT_STORAGE_ACCOUNT/g" ${deploy_containerapp_template_yaml} > bin/deploy_containerapp.yaml
sed -i "s/SED_OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING/${output_storage_connectionstring}/g" ${deploy_containerapp_template_yaml} > bin/deploy_containerapp.yaml
sed -i "s/SED_OUTPUT_STORAGE_CONTAINER/$OUTPUT_STORAGE_CONTAINER/g" ${deploy_containerapp_template_yaml} > bin/deploy_containerapp.yaml
sed -i "s/SED_IMAGE_URL/$IMAGE_URL/g" ${deploy_containerapp_template_yaml} > bin/deploy_containerapp.yaml
sed -i "s/SED_MANAGED_ENVIRONMENT_ID/$managed_environment_id/g" ${deploy_containerapp_template_yaml} > bin/deploy_containerapp.yaml

az containerapp create --name $CONTAINERAPP_NAME --resource-group $APP_RESOURCE_GROUP \
    --yaml ${deploy_containerapp_yaml} \
    --environment ${managed_environment_id}
