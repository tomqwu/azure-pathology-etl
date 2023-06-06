import os
import datetime
import json
import logging
import random
from flask import Flask, request
from wsidicomizer import WsiDicomizer
from azure.storage.blob import BlobServiceClient
from pydicom import dcmread
import shutil

# Constants
AFS_MOUNT_PATH = "/blobs"
DICOM_DIR_PREFIX = "dicom"
DCM_DIR_PREFIX = "dcm"

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

# Flask app
app = Flask(__name__)

# Environment variables
input_storage_account_connection_string = os.environ.get(
    "INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING"
)
input_storage_container_name = os.environ.get("INPUT_STORAGE_CONTAINER", "input")
output_storage_account_connection_string = os.environ.get(
    "OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING"
)
output_storage_container_name = os.environ.get("OUTPUT_STORAGE_CONTAINER", "output")
afs_mount_path = os.environ.get("AFS_MOUNT_PATH", AFS_MOUNT_PATH)

# Check required environment variables
required_vars = [
    "INPUT_STORAGE_ACCOUNT_CONNECTIONSTRING",
    "OUTPUT_STORAGE_ACCOUNT_CONNECTIONSTRING",
]

for var in required_vars:
    if os.getenv(var) is None:
        logger.error("Missing required environment variable %s", var)
        exit(1)


@app.route("/queueinput", methods=["POST"])
def incoming():
    """Handles incoming POST requests."""
    try:
        data = request.get_json()
        logger.info("Message Received: %s", data)

        url = data.get("data", {}).get("url")
        if url is None:
            raise ValueError("Invalid data: 'data.url' field is required")

        logger.info("Blob File created uploaded: %s", url)

        blob_name = url.split("/")[-1]
        logger.info("Blob Name: %s", blob_name)

        input_dir_path = create_dir(DICOM_DIR_PREFIX)
        output_dir_path = create_dir(DCM_DIR_PREFIX)
        download_file_path = get_blob_to_afs(blob_name, input_dir_path)

        etl_init()

        wsi_convert(download_file_path, output_dir_path)

        list_files_in_dir(input_dir_path)
        list_files_in_dir(output_dir_path)

        logger.info("Uploading files to output storage account")

        upload_dcm_files_to_output_storage_account(output_dir_path)

        logger.info("DICOM to WSI conversion completed successfully!")

        cleanup(input_dir_path, output_dir_path)

        return "Incoming message successfully processed!", 200

    except Exception as e:
        logger.error("Failed to process request: %s", str(e))
        return {"error": str(e)}, 400


def wsi_convert(download_file_path, output_dir_path):
    """Converts blob file to dcm file."""
    WsiDicomizer.convert(download_file_path, output_dir_path)


def cleanup(input_dir_path, output_dir_path):
    """Removes the input and output directories."""
    shutil.rmtree(input_dir_path)
    shutil.rmtree(output_dir_path)
    logger.info("Cleanup completed successfully!")

def etl_init():
    BLOBS_DIR = "/blobs"

    # remove all files and folders inside BLOBS_DIR
    for filename in os.listdir(BLOBS_DIR):
        file_path = os.path.join(BLOBS_DIR, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def create_dir(prefix_name):
    """Creates a directory in the Azure file share mount path."""
    dir_path = os.path.join(
        afs_mount_path, f"{prefix_name}-{datetime.datetime.now():%Y-%m-%d-%H%M%S}"
    )
    os.makedirs(dir_path, exist_ok=True)
    logger.info("Directory '%s' created.", dir_path)
    return dir_path


def list_files_in_dir(dir_path):
    """Lists the files in a directory."""
    logger.info("File List in %s directory:", dir_path)
    try:
        for file in os.listdir(dir_path):
            logger.info(file)
    except FileNotFoundError:
        logger.error("The directory '%s' does not exist.", dir_path)


def get_blob_to_afs(blob_name, input_dir_path):
    """Downloads a blob to the Azure file share."""
    blob_service_client = BlobServiceClient.from_connection_string(
        input_storage_account_connection_string
    )
    blob_client = blob_service_client.get_blob_client(
        container=input_storage_container_name, blob=blob_name
    )
    download_file_path = os.path.join(input_dir_path, blob_name)

    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    logger.info("Downloaded blob '%s' to '%s'", blob_name, download_file_path)

    return download_file_path


def insert_patient_id(dcm_file_path):
    """Inserts a patient ID into a .dcm file."""
    dcm_file = dcmread(dcm_file_path)
    dcm_file.PatientID = str(random.randint(1000000, 9999999))
    dcm_file.save_as(dcm_file_path)
    logger.info("Inserted patient id '%s' to '%s'", dcm_file.PatientID, dcm_file_path)


def upload_dcm_files_to_output_storage_account(output_dir_path):
    """Uploads .dcm files to the output storage account."""
    blob_service_client = BlobServiceClient.from_connection_string(
        output_storage_account_connection_string
    )

    for file in os.listdir(output_dir_path):
        blob_path = os.path.join(output_dir_path, file)
        insert_patient_id(blob_path)
        blob_client = blob_service_client.get_blob_client(
            container=output_storage_container_name, blob=file
        )

        with open(blob_path, "rb") as data:
            blob_client.upload_blob(data)

        logger.info("Uploaded blob '%s' to '%s'", file, output_storage_container_name)


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "localhost")
    port = int(os.getenv("APP_PORT", 6000))
    app.run(host=host, port=port, debug=False)
