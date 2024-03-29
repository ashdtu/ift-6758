"""
This assignment is based off of Greg Baker's data science course at SFU

All areas which require work are marked with a "TODO" flag.
"""
import numpy as np


def city_lowest_precipitation(totals: np.array) -> int:
    """
    Given a 2D array where each row represents a city, and each column is a month Jan-Dec of a
    particular year, return the city with the lowest total precipitation.
    """
    return int(np.argmin(np.sum(totals, axis=1)))


def avg_precipitation_month(totals: np.array, counts: np.array) -> np.array:
    """
    Determine the average precipitation in these locations for each month. That will be the total
    precipitation for each month (axis 0), divided by the total observations for that months.
    """

    total_per_month_across_cities = np.sum(totals, axis=0)
    count_per_month_across_cities = np.sum(counts, axis=0)
    return total_per_month_across_cities/count_per_month_across_cities


def avg_precipitation_city(totals: np.array, counts: np.array) -> np.array:
    """
    Do the same for the cities: give the average precipitation (daily precipitation averaged over
    the month) for each city.
    """

    total_per_city_across_months = np.sum(totals, axis=1)
    count_per_city_across_months = np.sum(counts, axis=1)
    return total_per_city_across_months / count_per_city_across_months


def quarterly_precipitation(totals: np.array) -> np.array:
    """
    Calculate the total precipitation for each quarter in each city (i.e. the totals for each
    station across three-month groups). You can assume the number of columns will be divisible by 3.

    Hint: use the reshape function to reshape to a 4n by 3 array, sum, and reshape back to n by 4.
    """
    if totals.shape[1] != 12:
        raise NotImplementedError("Input array does not have 12 months!")

    quarterly_total = totals.reshape((totals.shape[0], int(totals.shape[1]/3), 3))
    quarterly_total = np.sum(quarterly_total, axis=2)
    return quarterly_total


def main():
    data = np.load("data/monthdata.npz")
    totals = data["totals"]
    counts = data["counts"]

    # You can use this to steer your code
    # print(f"Row with the lowest precipitation:\n{city_lowest_precipitation(totals)}")
    # print(f"Average precipitation per month:\n{avg_precipitation_month(totals, counts)}")
    # print(f"Average precipitation per city:\n{avg_precipitation_city(totals, counts)}")
    print(f"Quarterly precipitation:\n{quarterly_precipitation(totals)}")


if __name__ == "__main__":
    main()
