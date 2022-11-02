"""
This assignment is based off of Greg Baker's data science course at SFU

All areas which require work are marked with a "TODO" flag.
"""
from typing import Tuple
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import scipy.stats as sp
import sys

sns.set()


OUTPUT_TEMPLATE = (
    "Initial (invalid) T-test p-value:\t\t{initial_ttest_p:.3g}\n"
    "Original data normality p-values:\t\t{initial_weekday_normality_p:.3g}, {initial_weekend_normality_p:.3g}\n"
    "Original data equal-variance p-value:\t\t{initial_levene_p:.3g}\n"
    "Transformed data normality p-values:\t\t{transformed_weekday_normality_p:.3g}, {transformed_weekend_normality_p:.3g}\n"
    "Transformed data equal-variance p-value:\t{transformed_levene_p:.3g}\n"
    "Weekly data normality p-values:\t\t\t{weekly_weekday_normality_p:.3g}, {weekly_weekend_normality_p:.3g}\n"
    "Weekly data equal-variance p-value:\t\t{weekly_levene_p:.3g}\n"
    "Weekly T-test p-value:\t\t\t\t{weekly_ttest_p:.3g}\n"
    "Mann-Whitney U-test p-value:\t\t\t{utest_p:.3g}"
)

def read_data(path: str) -> pd.DataFrame:
    # do not modify
    return pd.read_json(path, lines=True) 


def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # do not modify
    wd = df.query("is_weekend==False")
    we = df.query("is_weekend==True")
    return wd, we


def draw_histogram(df: pd.DataFrame, title: str = None) -> Figure:
    # do not modify
    fig, ax = plt.subplots(1, 1, dpi=100)
    ret = sns.histplot(data=df, x='comment_count', hue='is_weekend', ax=ax)
    if title:
        ret.set(title=title)
    return fig


# TODO - complete this method!
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process the raw DataFrame:

        1. Only keep the 'canada' subreddit
        2. Only keep the years 2012 and 2013
        3. Add a new column 'is_weekend' with a boolean True/False value 
    
    Args:
        df (pd.DataFrame): dataframe to process; contains the columns
            'date', 'subreddit', 'comment_count' by default

    Returns:
        pd.DataFrame: Must have (at minimum) the columns: 'comment_count', 'date', 'is_weekend'
    """
    df = df.copy()  # copy so you don't modify the original dataframe
    
    # TODO: filter on years, subreddit, and add an 'is_weekend' boolean column

    df = df[df.subreddit == "canada"]
    df = df[df["date"].dt.year.isin([2012, 2013])]
    df["is_weekend"] = df["date"].dt.weekday
    df["is_weekend"] = df["is_weekend"].isin([5, 6])
    return df


# TODO - complete this method!
def tests(wd: pd.DataFrame, we: pd.DataFrame, verbose: bool = False) -> Tuple[float, float, float, float]:
    """Does a T-tests between the two inputs, checking if the mean of the two distributions are
    the same. Also checks if both of the input datasets are normally distributed, and have the same 
    variance (a requirement for the T-test).

    Reference: https://docs.scipy.org/doc/scipy/reference/stats.html#statistical-tests

    Args:
        wd (pd.DataFrame): weekday data
        we (pd.DataFrame): weekend data
        verbose (bool): print the results

    Returns:
        Tuple[float, float, float, float]: p_ttest, p_wd_isnormal, p_we_isnormal, p_vartest
    """
    p_ttest, p_wd_normal, p_we_normal, p_vartest = None, None, None, None
    
    # TODO: get the p value for the t-test
    stat_ttest, p_ttest = sp.ttest_ind(wd["comment_count"].values, we["comment_count"].values)

    # TODO: get the p-value for the normal test on the weekday and weekend data separately
    # i.e. are both of these distributions normal?
    stat_wd_normal, p_wd_normal = sp.normaltest(wd["comment_count"].values)
    stat_we_normal, p_we_normal = sp.normaltest(we["comment_count"].values)

    # TODO: get the p-value for the test which checks whether these two distributions have the 
    # same variance
    stat_vartest, p_vartest = sp.levene(wd["comment_count"].values, we["comment_count"].values)
    # ---------- DO NOT MODIFY THIS FUNCTION BELOW THIS LINE ---------- #

    if verbose:
        print(f"p_value:\t{p_ttest.round(5)}")
        print(f"WD normality:\t{p_wd_normal.round(5)}")
        print(f"WE normality:\t{p_we_normal.round(5)}")
        print(f"Variance test:\t{p_vartest.round(5)}")

    return p_ttest, p_wd_normal, p_we_normal, p_vartest


# TODO - complete this method!
def central_limit_theorem(df: pd.DataFrame) -> pd.DataFrame:
    """Combine all weekdays and weekend days from each year/week pair and take the mean of their 
    (non-transformed) counts.

    Hints: you can get a “year” and “week number” from the first two values returned by 
    date.isocalendar(). This year and week number will give you an identifier for the (year, week). 
    Use Pandas to group by that value, and aggregate taking the mean. 
    
    Note: the year returned by isocalendar isn't always the same as the date's year (around the new 
    year). Use the year from isocalendar, which is correct for this. This is different than the
    year you used to filter the events; do not do any additional filtering!

    Args:
        df (pd.DataFrame): Cleaned dataframe containing (at minimum) the columns: 
            'date', 'comment_count', 'is_weekend'

    Returns:
        pd.DataFrame: Must have (at minimum) the columns: 'comment_count', 'is_weekend'
    """
    df = df.copy()

    # TODO: Combine all weekdays and weekend days from each year/week pair and take the mean of their counts
    df["year-week"] = df["date"].apply(lambda x: x.isocalendar()[:2])
    clt = df.groupby(by=["year-week", "is_weekend"]).mean()
    return clt


# TODO - complete this method!
def mann_whitney_u_test(wd: pd.DataFrame, we: pd.DataFrame) -> float:
    """Run the Mann-Whitney U-test between the weekday and weekend data.

    The Mann-Whitney U-test is a non-parametric test that can be used to decide that samples from 
    one group are larger/smaller than another. It assumes only two groups with:
        - Observations that are independent
        - Values are ordinal (can be sorted)

    Recall that the alternative hypothesis for a 'two-sided' states: 
        Given F(u) and G(u) as the cumulative distribution functions of the distributions 
        underlying x and y, respectively. Then the alternative hypothesis is that the distributions 
        are not equal, i.e. F(u) ≠ G(u) for at least one u.

    Args:
        wd (pd.DataFrame): weekday data
        we (pd.DataFrame): weekend data

    Returns:
        float: p-value of the Mann-Whitney-U test
    """
    # TODO

    stat, p_utest = sp.mannwhitneyu(wd["comment_count"], we["comment_count"])
    return p_utest


def main():
    """ 
    Note: nothing in main() will be marked, this is just to help steer your code.
    """
    path = "./data/reddit-counts.json.gz"
    if len(sys.argv) > 1:
        path = sys.argv[1]

    # load data
    raw_df = read_data(path)

    # preliminary processing
    df = process_data(raw_df)
    wd, we = split_data(df)
    p_ttest, p_wd_normal, p_we_normal, p_vartest = tests(wd, we)

    # fix 1: best transformed tests
    trans = df.copy()

    trans['comment_count'] = trans.comment_count  # TODO: apply some transformation to the data

    T_wd, T_we = split_data(trans)
    p_T_ttest, p_T_wd_normal, p_T_we_normal, p_T_vartest = tests(T_wd, T_we)

    # fix 2: central limit theorem tests
    clt = central_limit_theorem(df)
    clt_wd, clt_we = split_data(clt)
    p_clt_ttest, p_clt_wd_normal, p_clt_we_normal, p_clt_vartest = tests(clt_wd, clt_we)

    # fix 3: u tests on original data
    p_utest = mann_whitney_u_test(wd, we)


    print(OUTPUT_TEMPLATE.format(
        initial_ttest_p = p_ttest,

        initial_weekday_normality_p = p_wd_normal,
        initial_weekend_normality_p = p_we_normal,
        initial_levene_p = p_vartest,

        transformed_weekday_normality_p = p_T_wd_normal,
        transformed_weekend_normality_p = p_T_we_normal,
        transformed_levene_p = p_T_vartest,

        weekly_weekday_normality_p=p_clt_wd_normal,
        weekly_weekend_normality_p=p_clt_we_normal,
        weekly_levene_p=p_clt_vartest,
        weekly_ttest_p=p_clt_ttest,

        utest_p = p_utest,
    ))

if __name__ == '__main__':
    main()
