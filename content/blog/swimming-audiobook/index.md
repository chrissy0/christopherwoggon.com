+++
title = "Improving Audiobooks on Shokz OpenSwim"
date = "2024-04-01"
+++

If you’re anything like me, you love swimming. Recently, this hobby of mine has gotten a massive upgrade when I ordered the Shokz OpenSwim headphones.

While great for music, for me, the real strength of these headphones is allowing me to listen to podcasts and audiobooks during my workouts. While workouts at the gym are usually too intense to focus, swimming while learning about new topics is great.

Due to Bluetooth not working in water, these headphones are basically MP3 players. This seemed a bit annoying to me at first, but by now I love having a separate device, allowing me to immerse myself in a podcast or book without constant interruptions.

One feature I’m missing is skipping ahead or back inside a single track, for example a 7 hour audiobook. This post explores how to get around this limitation.

My workaround is chopping up long MP3s like podcasts and audiobooks into 2 minute chunks. This essentially turns the skip track functionality into a skip ahead function, allowing me to skip ahead and crucially rewind a piece of media in two minute increments.

The code I’ve written for this purpose also increases the volume of the audio file, as conversation is sometimes hard to hear while swimming. Bonus tip: Enable swimming mode before starting your workout. This makes conversation more clear.

The following function increases the volume of an MP3 file:

```python
import json
import subprocess


def normalize_volume(input_path, output_path, target_loudness=-12.0):
    analyze_cmd = [
        'ffmpeg', '-i', input_path, '-af',
        f'loudnorm=I={target_loudness}:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'
    ]
    analyze_result = subprocess.run(analyze_cmd, capture_output=True, text=True)

    result = ""
    lines = analyze_result.stderr.splitlines()
    begun = False
    for line in lines:
        if begun or line == "{":
            begun = True
            result += line
    loudnorm_stats = json.loads(result.split('[out#')[0])

    normalization_params = f'loudnorm=I={target_loudness}:TP=-1.5:LRA=11:measured_I={loudnorm_stats["input_i"]}:measured_LRA={loudnorm_stats["input_lra"]}:measured_TP={loudnorm_stats["input_tp"]}:measured_thresh={loudnorm_stats["input_thresh"]}:offset={loudnorm_stats["target_offset"]}:linear=true:print_format=json'

    normalization_cmd = [
        'ffmpeg', '-i', input_path, '-af', normalization_params, output_path
    ]
    subprocess.run(normalization_cmd)
```

This snippet invokes a function which splits the MP3 file into chunks, indirectly increasing audio levels by calling the previously defined function:
```python
from pydub import AudioSegment
import math
import os

def split_and_normalize(source_file, output_folder, split_length):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio = AudioSegment.from_mp3(source_file)

    total_length_seconds = len(audio) / 1000
    num_splits = math.ceil(total_length_seconds / (split_length * 60))

    source_file_name = source_file.split("/")[-1][:-4]

    for i in range(num_splits):
        start_ms = i * split_length * 60 * 1000
        end_ms = min((i + 1) * split_length * 60 * 1000, len(audio))
        split_audio = audio[start_ms:end_ms]
        split_filename = f"{output_folder}/{source_file_name}_{str(i+1).zfill(5)}.mp3"
        normalized_filename = f"{output_folder}/{source_file_name}_{str(i+1).zfill(5)}_normalized.mp3"
        split_audio.export(split_filename, format="mp3")
        normalize_volume(split_filename, normalized_filename)
        os.unlink(split_filename)


if __name__ == "__main__":
    source_file = "/location/of-my/audio_file.mp3"
    output_folder = "/location/of-output-files"
    split_length = 2

    split_and_normalize(source_file, output_folder, split_length)
```

Another problem I've encountered is that playback is ordered by the date and time MP3 files are copied. Not only is it slow and annoying to copy hundreds of individual MP3 files one by one to ensure proper order, which is essential for content such as audiobooks and podcasts, sometimes the order is still messed up if copying one MP3 split is initiated before another copy operation is finished. I have written the following script to easily copy all files in order.

```python
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
```

`os.sync()` is called after every file, ensuring that the previous copy operation has finished before the next one is initiated. Without this, the order is still messed up from time to time.

One downside of the Shokz OpenSwim I was unable to solve is that skipping to another folder to listen to music or some other content, and then coming back to the audiobook or podcast, causes the device to start at the beginning of the original audio file. Thus, it's usually best to stick to and finish one piece of content before moving on to other folders.

You can download the first script (splitting, increasing volume) <a href="shokz_openswim_splitting_and_volume_script.py" download>here</a> and the second script (copying) <a href="shokz_openswim_copy_script.py" download>here</a>.

Hopefully this helps someone :)

Chris

### Update: First user (30th of September 2024)

Today I've helped a reader set up the scripts on Windows. It made me realize how much work is necessary to make it work on a non-unix system. Still, we got it to work in the end. Glad I could help someone.

