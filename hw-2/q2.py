import os

import youtube_dl
import ffmpeg
import pandas as pd
import numpy as np
import csv
import threading
from tqdm import tqdm
from os.path import exists


def download_audio(YTID: str, path: str) -> None:
    """
    Create a function that downloads the audio of the Youtube Video with a given ID
    and saves it in the folder given by path. Download it as an mp3. If there is a problem downloading the file, handle the exception. If a file at `path` exists, the function should return without attempting to download it again.

    ** Use the library youtube_dl: https://github.com/ytdl-org/youtube-dl/ **
    Args:
      YTID: Contains the youtube ID, the corresponding youtube video can be found at
      'https://www.youtube.com/watch?v='+YTID
      path: The path to the file where the audio will be saved
    """
    # TODO
    if exists(path):
        print("File already exists: {}".format(path))
        return None

    ydl_options = {'format': "bestaudio/best",
                   'outtmpl': path,
                   'postprocessors': [{
                       'key': 'FFmpegExtractAudio',
                       'preferredcodec': 'mp3'}]
                   }
    try:
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.download(['https://www.youtube.com/watch?v=' + YTID])
    except Exception as e:
        print("Failed to download ID: {} with exception: {}".format(YTID, e))



def cut_audio(in_path: str, out_path: str, start: float, end: float) -> None:
    """
    Create a function that cuts the audio from in_path to only include the segment from start to end and saves it to out_path.

    ** Use the ffmpeg library: https://github.com/kkroening/ffmpeg-python
    Args:
      in_path: Path of the audio file to cut
      out_path: Path of file to save the cut audio
      start: Indicates the start of the sequence (in seconds)
      end: Indicates the end of the sequence (in seconds)
    """
    # TODO
    if not os.path.exists(in_path):
        return None
    try:
        inp_audio = ffmpeg.input(in_path)
        cut_audio = inp_audio.audio.filter('atrim', start=start, end=end)
        out_audio = ffmpeg.output(cut_audio, out_path)
        ffmpeg.run(out_audio)
    except Exception as e:
        print("failed with error: {}".format(e))
