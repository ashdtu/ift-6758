"""
All areas which require work are marked with a "TODO" flag.
"""
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
from tqdm.autonotebook import tqdm
from typing import Tuple
import xml.etree.ElementTree as ET


# TODO - complete this method!
def parse_xml(path: str) -> pd.DataFrame:
    """_summary_
    Parse the XML file obtained from the FIDE player database which can be found here:

        http://ratings.fide.com/download.phtml?period=2022-10-01
    
    Note that the ratings are updated fairly regularly, so we are using the fixed timestamp of
    06 Oct 2022, which is provided for you in the data directory. You should not need to download
    anything.

    Args:
        path (str): Path to the desired .xml file; if it does not exist, automatically search for
            the corresponding .zip file to extract

    Returns:
        pd.DataFrame: DataFrame containing the raw data from the xml file, with the columns:
            ["name", "rating", "sex", "birthday", "country", "flag", "title"]
    """
    path = Path(path)

    # unzip xml data if unavailable
    if not path.is_file():
        if path.with_suffix(".zip").is_file():
            shutil.unpack_archive(path.with_suffix(".zip"), path.parent)
        else:
            raise FileNotFoundError("%s nor an archive exists." % path)

    # define function to extract value, define tags to extract 
    _get_val = lambda entry, tag: entry.find(tag).text
    TARGET_ATTRIBUTES = ["name", "rating", "sex", "birthday", "country", "flag", "title"]

    # ---------- DO NOT MODIFY THIS FUNCTION ABOVE THIS LINE ---------- #

    # TODO: 
    # XML element tree (use xml.etree.ElementTree)
    xml_tree = ET.parse(path)
    xml_tree = xml_tree.getroot()

    # TODO: iterate over the root node, get the desired values for the desired tags
    # Make sure you load all of the values in TARGET_ATTRIBUTES (use the same column name in the
    # dataframe as the tag name!). You can use the provided _get_val(person, tag) method defined 
    # above to get the corresponding tag.
    player_list = []

    for player in xml_tree:
        player_list.append([_get_val(player, tag) for tag in TARGET_ATTRIBUTES])
   
    # TODO: convert into a dataframe
    df = pd.DataFrame(player_list, columns=TARGET_ATTRIBUTES)
    return df


# TODO - complete this method!
def clean_data(df: pd.DataFrame, year_cutoff: int) -> pd.DataFrame:
    """_summary_

    Args:
        df (pd.DataFrame): the raw dataframe as returned from the parse_xml() method
        year_cutoff (int): remove players with birthdays GREATER THAN (>) this value; i.e. only 
            include players born up to (and including) this year

    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    # TODO: drop data with no birthday information
    df = df.dropna(subset=["birthday"])

    # TODO: convert the numeric types into integers
    df = df.astype({"birthday": int, "rating": int})

    # TODO: only keep players with birthdays up to year_cutoff (inclusive)
    df = df[df.birthday <= year_cutoff]
    return df


# TODO - complete this method!
def bin_counts(df: pd.DataFrame, bins: list, bin_centers: list) -> pd.DataFrame:
    """Returns a dataframe with the `ratings` binned between the values given in `bins`, and
    with a label given in `bin_centers`. In addition to the raw count, also add a normalized bin
    count column named `count_norm` by dividing the counts by the sum of counts. 

    Eg: Given 
        >>  x           = pd.DataFrame({'rating': [1, 2, 4, 6, 6, 7, 8, 11]})
        >>  bins        = [0, 5, 10, 15]
        >>  bin_centers = [2.5, 7.5, 12.5]
    
    bin_counts(x, bins, bin_centers) should return:
        >>      rating  count  count_norm
        >>  0    7.5      4       0.500
        >>  1    2.5      3       0.375
        >>  2   12.5      1       0.125

    Args:
        df (pd.DataFrame): Cleaned dataframe with at least the 'rating' column
        bins (list): Defines the bin edges; i.e. [0, 5, 10] defines two bins: [0, 5), and [5, 10)
        bin_centers (list): Defines the labels that will be used; i.e. [2.5, 7.5] for the above 
            example will bin values as [0, 5) -> 2.5, and [5, 10) -> 7.5.

    Returns:
        pd.DataFrame: dataframe with binned values; must have the columns 
            ['rating', 'count', 'count_norm']. Rename them if necessary.
    """
    if 'rating' not in df.keys():
        raise ValueError("Incorrect input format; 'rating' must be a column in the input dataframe")

    # TODO: hint - use pd.cut, and make sure to use reset_index() when relevant
    hist = None
    df["binned_rating"] = pd.cut(df["rating"], bins=bins, labels=bin_centers)
    hist = df.groupby(by=["binned_rating"]).count()
    hist = hist.reset_index(level=0)

    # TODO: rename the columns; make sure they're still meaningful (we want 'rating', 'count')
    hist = hist.rename(columns={"rating": "count",
                                "binned_rating": "rating"})

    # TODO: add the 'count_norm' column
    hist["count_norm"] = hist["count"].apply(lambda x: x/hist["count"].sum())
    hist = hist.sort_values(by=["count"],ascending=False)
    hist = hist.reset_index(drop=True)
    return hist[["rating", "count", "count_norm"]]


class PermutationTest:
    def __init__(self, df: pd.DataFrame, n_overrep: int, n_underrep: int):
        """Implements the permutation test experiment.

        Args:
            df (pd.DataFrame): Full dataframe to partition (i.e. includes both groups)
            n_overrep (int): Number of elements in the overrepresented group
            n_underrep (int): Number of elements in the underrepresented group
        
        n_overrep + n_underrep should be == len(df)! Technically < len(df) is okay too...
        """
        if len(df) < n_overrep + n_underrep:
            raise ValueError(f"Sum of n_overrep + n_underrep must be <= len(df)")
        self.df = df
        self.n_overrep = n_overrep
        self.n_underrep = n_underrep
    
    # TODO - complete this method!
    def job(self, seed: int = None) -> Tuple[int, int]:
        """ Samples two groups of size n_overrep, n_underrep and returns the max rating for each
        group in that order (overrep, underrep)

        Args:
            seed (int, optional): sets the random state, if specified.

        Returns:
            Tuple[int, int]: the maximum ratings for each of the two groups, in the order 
                (max(overrep), max(underrep))
        """
        if seed is not None:
            np.random.seed(seed)
            
        # TODO: sample two groups of size n_overrep, n_underrep and return the max rating for each
        # group in the order (overrep, underrep)

        indexes = list(range(len(self.df)))
        shuffled_indexes = np.random.permutation(indexes)
        overrepresented_df = self.df.iloc[shuffled_indexes[:self.n_overrep]]
        underrepresented_df = self.df.iloc[shuffled_indexes[self.n_overrep:self.n_overrep + self.n_underrep]]

        max_rating_overepresented = max(overrepresented_df.rating.values)
        max_rating_underrepresented = max(underrepresented_df.rating.values)
        return max_rating_overepresented, max_rating_underrepresented


# TODO - complete this method!
def sample_two_groups(
    df: pd.DataFrame, n_overrep: int, n_underrep: int, n_iter: int=1000
) -> Tuple[np.array, np.array]:
    """Run n_iter permutation tests on df, split into two groups (sampled WITHOUT replacement) of
    size n_overrep, and n_underrep. Returns two arrays of length n_iter, which corresponds to the
    maximum rating in the over and under-represented groups respectively. 

    Args:
        df (pd.DataFrame): cleaned dataframe to process
        n_overrep (int): number of samples for the overrepresented group
        n_underrep (int): number of samples for the underrepresented group
        n_iter (int, optional): The total number of iterations to run this for

    Returns:
        Tuple[np.array, np.array]: Two arrays containing the maximums for the over and under
            represented groups for each of the n_iter experiments.
    """
    best_over = []
    best_under = []

    # TODO: run n_iter runs of this experiment, and return a numpy array containing the maxes of 
    # the over and under-represented groups respectively. 

    # Tip: wrap your iterator with tqdm to get a progress bar, eg:
    # >>> for i in tqdm(range(10)):
    # >>>     print(i)

    p_test = PermutationTest(df=df, n_overrep=n_overrep, n_underrep=n_underrep)
    for i in tqdm(range(n_iter)):
        max_over, max_under = p_test.job()
        best_over.append(max_over)
        best_under.append(max_under)

    return np.array(best_over), np.array(best_under)


