import os
import uuid
import json

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

azure_conn_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(azure_conn_str)

kitchen_container = "kitchen" + str(uuid.uuid4()) 
bedroom_container = "bedroom" + str(uuid.uuid4()) 
file_path = "/home/pi/Desktop/wav_files/zip_files"
file_name = "202004061233.zip"

container_names = [kitchen_container,
                   bedroom_container]

try:
    
    print("Creating containers and uploading zip file")
    for container_name in container_names:
        print(F"Creating and uploading zip file to {container_name}")
        container_client = blob_service_client.create_container(container_name)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    
    # Upload the created file
        with open(os.path.join(file_path, file_name), "rb") as data:
            blob_client.upload_blob(data)
          
    print("Finished uploading file")

    container_dict = {
        'kitchen': kitchen_container,
        'bedroom': bedroom_container,
        'AZURE_STORAGE_CONNECTION_STR':azure_conn_str,
    }

    print("Outputting container json")
    container_json = json.dumps(container_dict)
    with open('container_settings.json', 'w') as outfile:
            outfile.write(container_json)
  
except Exception as ex:
    print('Exception:')
    print(ex)

