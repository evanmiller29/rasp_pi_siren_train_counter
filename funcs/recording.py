import os
import pyaudio
import wave

def find_mic_usb_port():
    audio =pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        dev_info = audio.get_device_info_by_index(i).get('name')
        print(F'Index #{i} - name = {dev_info}')
            
        if dev_info.split(':')[0] == 'USB Audio Device': return i

def record_from_mic(settings_dict,
                    wave_output_filename):
    
    audio =pyaudio.PyAudio()

    stream = audio.open(format=settings_dict['form'],
                        rate=settings_dict['sample_rate'],
                        channels=settings_dict['channel'],
                        input_device_index=settings_dict['usb_audio_device_num'],
                        frames_per_buffer=settings_dict['chunk_size'],
                        input=True,)

    print('Recording')
    frames = []
    for j in range(0, int(settings_dict['sample_rate']/settings_dict['chunk_size']) * settings_dict['record_secs']):
        data = stream.read(settings_dict['chunk_size'], exception_on_overflow = False)
        frames.append(data)
        
    print('Finished recording')

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(os.path.join(settings_dict['output_dir'], wave_output_filename), 'wb') as wavefile:
        wavefile.setnchannels(settings_dict['channel'])
        wavefile.setsampwidth(audio.get_sample_size(settings_dict['form']))
        wavefile.setframerate(settings_dict['sample_rate'])
        wavefile.writeframes(b''.join(frames))
    

