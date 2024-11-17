import os
import shutil
from pathlib import Path

source_folder = "/path/to/audiobook-splits/folder/previously/generated/some_audiobook_you_want_to_listen_to"
target_folder = "/Volumes/OpenSwim/Books/Some Audibook You Want To Listen To"

mp3_files = sorted([f"{source_folder}/{file}" for file in os.listdir(source_folder) if file.endswith('.mp3')])

# create folder if non-existent
Path(target_folder).mkdir(parents=True, exist_ok=True)

for file in mp3_files:
    print(f"Copying {file}")
    command = f"cp \"{file}\" \"{target_folder}\""
    shutil.copy2(file, target_folder)
    os.sync()
