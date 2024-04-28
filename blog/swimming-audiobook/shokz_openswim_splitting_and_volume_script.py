from pydub import AudioSegment
import math
import os
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
    loudnorm_stats = json.loads(result)

    normalization_params = f'loudnorm=I={target_loudness}:TP=-1.5:LRA=11:measured_I={loudnorm_stats["input_i"]}:measured_LRA={loudnorm_stats["input_lra"]}:measured_TP={loudnorm_stats["input_tp"]}:measured_thresh={loudnorm_stats["input_thresh"]}:offset={loudnorm_stats["target_offset"]}:linear=true:print_format=json'

    normalization_cmd = [
        'ffmpeg', '-i', input_path, '-af', normalization_params, output_path
    ]
    subprocess.run(normalization_cmd)


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
