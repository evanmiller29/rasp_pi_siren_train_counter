import os
import pyaudio
import typer

from datetime import datetime
from pathlib import Path
from shutil import make_archive
from funcs.recording import find_mic_usb_port, record_from_mic
from run_settings import form_1, chans, samp_rate, chunk

app = typer.Typer()

@app.command()
def record_save_audio(n_files: int = 10,
                      record_secs: int = 60,
                      location: str = 'kitchen',
                      base_dir: str = '/home/pi/Desktop/wav_files'
                      ):
    
    # Directories
    output_dir = os.path.join(base_dir, 'raw_files')
    zip_file_dir = os.path.join(base_dir, 'zip_files') 

    # Creating a specific run time folder for wave files
    dt_file_start = datetime.now().strftime('%Y%m%d%H%M')
    out_dir_path = os.path.join(output_dir, dt_file_start)
    Path(out_dir_path).mkdir(parents=True, exist_ok=True)
    
    usb_audio_device_num = find_mic_usb_port()
    print(F'USB device number  = {usb_audio_device_num}')
    
    settings_dict = {
    'form': form_1,
    'channel': chans,
    'sample_rate': samp_rate,
    'chunk_size': chunk,
    'record_secs': record_secs,
    'usb_audio_device_num': usb_audio_device_num,
    'output_dir': out_dir_path
    }
    
    # Recording and saving down files
    for i in range(n_files):
        print(F'Outputting file number = {i+1}')
        
        dt_now = datetime.now().strftime('%Y%m%d%H%M%s')
        wave_output_filename = F'{dt_now}.wav'
        record_from_mic(settings_dict, wave_output_filename)
        
    # Zip the recorded audio to a file
    zip_file_dir = os.path.join(zip_file_dir, F'{dt_file_start}.zip')
    print(F'Zipping wave files to {zip_file_dir}')
    make_archive(zip_file_dir, 'zip', out_dir_path)

if __name__ == "__main__":
    app()