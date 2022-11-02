import re
import os
import pandas as pd
from tqdm import tqdm
from q2 import download_audio, cut_audio
from typing import List
from concurrent.futures import ThreadPoolExecutor


def filter_df(csv_path: str, label: str) -> pd.DataFrame:
    """
    Write a function that takes the path to the processed csv from q1 (in the notebook) and returns a df of only the rows 
    that contain the human readable label passed as argument

    For example:
    get_ids("audio_segments_clean.csv", "Speech")
    """
    # TODO
    df = pd.read_csv(csv_path)
    mask = [True if label in item.split('|') else False for item in df["label_names"].values]
    return df[mask]


def data_pipeline(csv_path: str, label: str) -> None:
    """
    Using your previously created functions, write a function that takes a processed csv and for each video with the given label:
    (don't forget to create the associated label folder!). 
    1. Downloads it to <label>_raw/<ID>.mp3
    2. Cuts it to the appropriate segment
    3. Stores it in <label>_cut/<ID>.mp3

    It is recommended to iterate over the rows of filter_df().
    Use tqdm to track the progress of the download process (https://tqdm.github.io/)

    Unfortunately, it is possible that some of the videos cannot be downloaded. In such cases, your pipeline should handle the failure by going to the next video with the label.
    """
    # TODO
    filtered_df = filter_df(csv_path, label)

    # Download audio files
    yt_ids = filtered_df["# YTID"].to_list()
    if not os.path.exists(f"{label}_raw"):
        os.mkdir(f"{label}_raw")
    download_paths = [f"{label}_raw/{vid_id}.mp3" for vid_id in yt_ids]

    func_iterable = tuple(zip(yt_ids, download_paths))
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda f: download_audio(*f), func_iterable), total=len(func_iterable)))

    # Cut and save audio
    start_times = filtered_df[" start_seconds"].to_list()
    end_times = filtered_df[" end_seconds"].to_list()
    if not os.path.exists(f"{label}_cut"):
        os.mkdir(f"{label}_cut")
    cut_audio_paths = [f"{label}_cut/{vid_id}.mp3" for vid_id in yt_ids]

    cut_func_iterable = tuple(zip(download_paths, cut_audio_paths, start_times, end_times))
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda f: cut_audio(*f), cut_func_iterable), total=len(cut_func_iterable)))


def rename_files(path_cut: str, csv_path: str) -> None:
    """
    Suppose we now want to rename the files we've downloaded in `path_cut` to include the start and end times as well as length of the segment. While
    this could have been done in the data_pipeline() function, suppose we forgot and don't want to download everything again.

    Write a function that, using regex (i.e. the `re` library), renames the existing files from "<ID>.mp3" -> "<ID>_<start_seconds_int>_<end_seconds_int>_<length_int>.mp3"
    in path_cut. csv_path is the path to the processed csv from q1. `path_cut` is a path to the folder with the cut audio.

    For example
    "--BfvyPmVMo.mp3" -> "--BfvyPmVMo_20_30_10.mp3"

    ## BE WARY: Assume that the YTID can contain special characters such as '.' or even '.mp3' ##
    """
    # TODO
    file_names = os.listdir(path_cut)
    df = pd.read_csv(csv_path)
    for orig_file_name in file_names:
        yt_id = orig_file_name[:-4]
        meta_data = df[df["# YTID"] == yt_id]
        start_time = int(meta_data[" start_seconds"].values[0])
        end_time = int(meta_data[" end_seconds"].values[0])
        duration_seg = end_time - start_time
        # new_file_name = f"{orig_file_name[:-4]}_{start_time}_{end_time}_{duration_seg}.mp3"
        new_file_name = re.sub(r"(?=\.[^\.]+$)", f"_{start_time}_{end_time}_{duration_seg}", orig_file_name)
        os.rename(os.path.join(path_cut, orig_file_name), os.path.join(path_cut, new_file_name))


if __name__ == "__main__":
    print(filter_df("audio_segments_clean.csv", "Laughter"))
    data_pipeline("audio_segments_clean.csv", "Laughter")
    rename_files("Laughter_cut", "audio_segments_clean.csv")

