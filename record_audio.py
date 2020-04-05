import pyaudio
import wave
import os
from datetime import datetime
from pathlib import Path
from shutil import make_archive

# Using as a poor mans argparse/typer. Will probs just use typer as I'll learn something
from run_settings import form_1, chans, samp_rate, chunk, record_secs, n_files

# Directories
base_dir = '/home/pi/Desktop/wav_files'
output_dir = os.path.join(base_dir, 'raw_files')
zip_file_dir = os.path.join(base_dir, 'zip_files') 

# Creating a specific run time folder for wave files
dt_file_start = datetime.now().strftime('%Y%m%d%H%M')
out_dir_path = os.path.join(output_dir, dt_file_start)
Path(out_dir_path).mkdir(parents=True, exist_ok=True)

# Finding the port for the USB audio device
audio =pyaudio.PyAudio()
for i in range(audio.get_device_count()):
    dev_info = audio.get_device_info_by_index(i).get('name')
    print(F'Index #{i} - name = {dev_info}')
        
    if dev_info.split(':')[0] == 'USB Audio Device': usb_audio_device_num = i
        
print(F'USB device number  = {usb_audio_device_num}')

# Recording and saving down files
for i in range(n_files):
    print(F'Outputting file number = {i+1}')
    
    dt_now = datetime.now().strftime('%Y%m%d%H%M%s')
    wave_output_filename = F'{dt_now}.wav'
    audio =pyaudio.PyAudio()

    stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                    input_device_index=usb_audio_device_num,
                    input=True, frames_per_buffer=chunk)

    print('Recording')
    frames = []
    for j in range(0, int(samp_rate/chunk) * record_secs):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)
        
    print('Finished recording')

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(os.path.join(out_dir_path, wave_output_filename), 'wb') as wavefile:
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))

# Zip the recorded audio to a file
zip_file_dir = os.path.join(zip_file_dir, F'{dt_file_start}.zip')
print(F'Zipping wave files to {zip_file_dir}')
make_archive(zip_file_dir, 'zip', out_dir_path)