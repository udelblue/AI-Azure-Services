import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
from fastapi import UploadFile

import os

class Storage:
    def __init__(self):
        self.connect_string = os.environ.get('STORAGE_ACCOUNT_CONNECTION_STRING')
        self.container = os.environ.get('STORAGE_ACCOUNT_CONTAINER')
     
    def upload_file(self, file):
        blob_service_client = BlobServiceClient.from_connection_string(self.connect_string) # type: ignore
        blob_client = blob_service_client.get_blob_client(container=self.container, blob=file.filename) # type: ignore
        return blob_client.upload_blob(file.file, overwrite=True, blob_type="BlockBlob")

    
    def download_file(self, file):
        blob_service_client = BlobServiceClient.from_connection_string(self.connect_string) # type: ignore
        blob_client = blob_service_client.get_blob_client(container='mycontainer)', blob='my_blob')
        with open(file, "wb") as data:
            data.write(blob_client.download_blob().readall())
        return file
    

    def get_blob_url(self, blob_name):
        blob_service_client = BlobServiceClient.from_connection_string(self.connect_string) # type: ignore
        blob_client = blob_service_client.get_blob_client(container=self.container, blob=blob_name) # type: ignore
        return blob_client.url


    def generate_sas_token(self, blob_name, expiry_hours=1):
        blob_service_client = BlobServiceClient.from_connection_string(self.connect_string) # type: ignore
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name, # type: ignore
            container_name=self.container, # type: ignore
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=expiry_hours) # type: ignore
        )
        return sas_token
    
    def get_public_url(self, blob_name):
        blob_service_client = BlobServiceClient.from_connection_string(self.connect_string) # type: ignore
        blob_client = blob_service_client.get_blob_client(container=self.container, blob=blob_name) # type: ignore
        sas_token = self.generate_sas_token(blob_name, expiry_hours=24)
        return f"{blob_client.url}?{sas_token}"
    
