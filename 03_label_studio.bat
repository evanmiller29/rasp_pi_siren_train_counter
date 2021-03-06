::call conda create --name rasp_pi_train python=3.7 -y
::call activate rasp_pi_train
::call pip install -r requirements_windows.txt

call label-studio init train_detection --input-path=../raw/unzipped/ --input-format=audio-dir --label-config=config.xml
call label-studio start train_detection 