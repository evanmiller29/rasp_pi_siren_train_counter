import os
import pyaudio
import typer
import json

from datetime import datetime
from pathlib import Path
from shutil import make_archive
from funcs.recording import find_mic_usb_port, record_from_mic
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# The output json of the create_blob_storage_containers.py is read in so I know
# Where to send the zip files
with open('container_settings.json') as json_file:
    container_loc_info = json.load(json_file)

# Read in azure information from container_settings and create client
azure_conn_str = container_loc_info['AZURE_STORAGE_CONNECTION_STRING']
blob_service_client = BlobServiceClient.from_connection_string(azure_conn_str)

# Setting up directores
base_dir = '/home/pi/Desktop/wav_files'
output_dir = os.path.join(base_dir, 'raw_files')
zip_file_dir = os.path.join(base_dir, 'zip_files') 

form_1 = pyaudio.paInt16
app = typer.Typer()

@app.command()
def record_save_audio(chans: int =1,
                      samp_rate: int = 44100,
                      chunk: int = 4096,                     
                      base_dir: str = '/home/pi/Desktop/wav_files',
                      n_files: str = typer.Option(['1','10', '30', '60', '120', '180'],
                                                  prompt='How many files would you like to record?'),
                      record_secs: str = typer.Option(['10','30', '60'],
                                                      prompt='How should each record be for?'),
                      location: str = typer.Option(['kitchen','bedroom'],
                                                   prompt='Where are you recording audio')
                      ):
    
    # Converting string n_files to int. This might seem odd but I can't get the CMD options to use integers, has to be strings
    # Casting the string numbers to integers so I can use them later
    n_files = int(n_files)
    record_secs = int(record_secs)

    # Creating a specific run time folder for wave files
    dt_file_start = datetime.now().strftime('%Y%m%d%H%M')
    out_dir_path = os.path.join(output_dir, dt_file_start)
    # Nerds on internet said this is safe than os.exists
    Path(out_dir_path).mkdir(parents=True, exist_ok=True)
    
    usb_audio_device_num = find_mic_usb_port()
    print(F'USB device number  = {usb_audio_device_num}')
    
    # Creating a settings dictionary so I can preserve key metadata
    # For use later on in audio processing
    settings_dict = {
    'form': form_1,
    'channel': chans,
    'sample_rate': samp_rate,
    'chunk_size': chunk,
    'record_secs': record_secs,
    'usb_audio_device_num': usb_audio_device_num,
    'output_dir': out_dir_path,
    'location': location
    }
            
    # Recording and saving down files
    for i in range(n_files):
        print(F'Outputting file number = {i+1}')
        
        dt_now = datetime.now().strftime('%Y%m%d%H%M%s')
        wave_output_filename = F'{dt_now}.wav'
        record_from_mic(settings_dict, wave_output_filename)
            
    print('Zipping the recorded audio to a file')
    # Takes the datetimestamped folder name in the raw directory and uses
    # that datetimestamp as the name for the zip archive
    wave_out_folder_datetime = os.path.join(zip_file_dir, F'{dt_file_start}')
    zip_file_name = wave_out_folder_datetime.split('/')[-1] + '.zip'
    
    print('Uploading data to Azure Blob storage')
    container_name = container_loc_info[location]
    
    # Telling Azure where to put the zip file. If the location folder doesn't exist it gets created
    # Otherwise it gets put into a folder that represents the current rasp pi dir
    # And it's a nightmare to find. So the parent folder is always gonna be kitchen/bedroom
    blob_loc = location + '/' + wave_out_folder_datetime + '.zip'
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_loc)
    
    # Adding the final settings to the dictionary before zipping directory
    settings_dict['zip_file'] = zip_file_name
    settings_dict['blob_loc'] = blob_loc
    
    print('Outputting settings JSON to directory')
    json_settings = json.dumps(settings_dict)
    with open(os.path.join(out_dir_path, 'settings.json'), 'w') as outfile:
        outfile.write(json_settings)
    
    # Making zip archive of .wav files as well as settings.json
    print(F'Zipping wave files to {zip_file_dir}')
    print(F'Zip file name = {zip_file_name}')
    make_archive(wave_out_folder_datetime, 'zip', out_dir_path)
    
    # No matter what I do I can't get the zips to output on Azure to /kitchen/
    # I've tried switching using os.chdir to /home/, uploading data to azure
    # but even that doens't work. I'd need to find something more about the azure procedure or
    # do a more dramatic folder switch (if that exists)
    # But honestly, now the zips are in the same folder, so that's a million times better than before.
    
    with open(os.path.join(zip_file_dir, zip_file_name), "rb") as data:
        blob_client.upload_blob(data)
    
if __name__ == "__main__":
    app()