import os
import datetime
import base64
import requests
import json
from gtts import gTTS
from io import BytesIO
from flask import Flask, request
from wsidicomizer import WsiDicomizer
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from pydicom import dcmread
import logging
import random

# Create a custom logger
logger = logging.getLogger(__name__)
# Set level of logger
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)

# Add handlers to the logger
logger.addHandler(c_handler)

app = Flask(__name__)

# code
input_storage_account = os.getenv("INPUT_STORAGE_ACCOUNT")

input_storage_account_connection_string = os.environ.get(
    "INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING"
)
input_storage_container_name = os.environ.get("INPUT_STORAGE_CONTAINER", "input")
output_storage_account = os.getenv("OUTPUT_STORAGE_ACCOUNT")
output_storage_account_connection_string = os.environ.get(
    "OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING"
)
output_storage_container_name = os.environ.get(
    "OUTPUT_STORAGE_CONTAINER", "output"
)
afs_mount_path = os.environ.get("AFS_MOUNT_PATH", "/blobs")

# exit app if missing required environment variables
if (
    input_storage_account_connection_string is None
    or output_storage_account_connection_string is None
):
    logger.error("Missing required environment variables")
    exit(1)

@app.route("/queueinput", methods=["POST"])
def incoming():
    try:
        incoming_text = request.get_data().decode()
        logger.info("Message Received: %s", incoming_text)

        # Parse JSON data and get URL
        data = json.loads(incoming_text)
        url = data.get("data", {}).get("url")
        if url is None:
            raise ValueError("Invalid data: 'data.url' field is required")

        logger.info("Blob File created uploaded: %s", url)

        # get last '/' position and assign rest of string to blob_name
        blob_name = url[url.rfind("/") + 1 :]
        logger.info("Blob Name: %s", blob_name)

        input_folder = create_folder("dicom")
        output_folder = create_folder("dcm")
        download_file_path = get_blob_to_afs(blob_name, input_folder)

        # convert blob file to dcm file
        wsi_convert(download_file_path, output_folder)

        list_files_in_folder(input_folder)
        list_files_in_folder(output_folder)

        logger.info("Uploading files to output storage account")

        upload_dcm_files_to_output_storage_account(output_folder)

        logger.info("DICOM to WSI conversion completed successfully!")

        cleanup(input_folder, output_folder)

        return "Incoming message successfully processed!"

    except Exception as e:
        logger.error("Failed to process request: %s", str(e))
        return {"error": str(e)}, 400  # HTTP 400 Bad Request response


# convert blob file to dcm file
def wsi_convert(download_file_path, output_folder):
    created_files = WsiDicomizer.convert(download_file_path, output_folder)


# rm input_folder and output_folder
def cleanup(input_folder, output_folder):
    os.rmdir(input_folder)
    os.rmdir(output_folder)
    logger.info("Cleanup completed successfully!")


def create_folder(prefix_name):
    # Azure file share is mounted as /blobs
    folder = (
        afs_mount_path
        + "/"
        + prefix_name
        + "-"
        + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    )
    try:
        # create the directory
        os.mkdir(folder)
        logger.info("Directory '%s' created.", folder)
    except FileExistsError:
        logger.info("Directory '%s' already exists.", folder)
    return folder


# List files in folder
def list_files_in_folder(folder):
    # print file list in folder
    logger.info("File List in %s folder", folder)
    try:
        # get list of files in the directory
        files = os.listdir(folder)

        # iterate over the files and print each one
        for file in files:
            logger.info(file)
    except FileNotFoundError:
        logger.error("The directory '%s' does not exist.", folder)


# Download blob to AFS
def get_blob_to_afs(blob_name, input_folder):
    try:
        # Create a blob client using the local file name as the name for the blob
        blob_service_client = BlobServiceClient.from_connection_string(
            input_storage_account_connection_string
        )

        blob_client = blob_service_client.get_blob_client(
            container=input_storage_container_name, blob=blob_name
        )
        download_file_path = os.path.join(input_folder, blob_name).replace(" ", "-")

        # Download the blob and write it to file
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        logger.info("Downloaded blob '%s' to '%s'", blob_name, download_file_path)

        return download_file_path
    except Exception as e:
        logger.error("Failed to download blob '%s': %s : %s : %s", blob_name, input_storage_container_name, input_storage_account_connection_string, str(e))
        return


# insert_patient_id (random 7 digitals) to dcm file
def insert_patient_id(dcm_file_path):
    try:
        patient_id = str(random.randint(1000000, 9999999))
        dcm_file = dcmread(dcm_file_path)
        dcm_file.PatientID = patient_id
        dcm_file.save_as(dcm_file_path)
        logger.info(
            "Inserted patient id '%s' to '%s'", dcm_file.PatientID, dcm_file_path
        )
    except Exception as e:
        logger.error("Failed to insert patient id '%s': %s", patient_id, str(e))
        return


# loop over output folder for each .cdm file, upload it to output_storage_account account under output container
def upload_dcm_files_to_output_storage_account(output_folder):
    try:
        # Create a blob client using the local file name as the name for the blob
        blob_service_client = BlobServiceClient.from_connection_string(
            output_storage_account_connection_string
        )
        # get list of files in the directory
        files = os.listdir(output_folder)
        # iterate over the files and print each one
        for file in files:
            blob_path = output_folder + "/" + file
            # fix patient_id before upload
            insert_patient_id(blob_path)

            blob_client = blob_service_client.get_blob_client(
                container=output_storage_container_name, blob=file
            )
            with open(blob_path, "rb") as data:
                blob_client.upload_blob(data)
            logger.info(
                "Uploaded blob '%s' to '%s'", file, output_storage_container_name
            )

    except Exception as e:
        logger.error("Failed to upload blob '%s': %s", file, str(e))
        return


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "localhost")
    port = int(os.getenv("APP_PORT", 6000))
    app.run(host=host, port=port, debug=False)
