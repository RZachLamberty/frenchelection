#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: representatives.py
Author: zlamberty
Created: 2017-04-29

Description:
    module for calculating number of representatives based on population

Usage:
    <usage>

"""

import os

import pandas as pd


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

HERE = os.path.realpath(os.path.dirname(__file__))
DATA = os.path.join(HERE, 'data')
FUS = os.path.join(DATA, 'us.ec.csv')
RPR = 435 / 50


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def num_reps(df, popColname='population', targetColname='num_reps',
             regionColname='state', repsPerRegion=RPR, baseline=1):
    """use the population values in df.popColname to create df.targetColname, a
    list of the number of representatives assigned to that record in the df
    based on its (and the total) population

    args:
        df (pandas.DataFrame): a dataframe with population information
        popColname (str): the column name of the population information within
            input dataframe df
        targetColname (str): the desired column name of the calculated electoral
            votes values
        regionColname (str): the column name of the region variable (needed for
            group by statement to calculate final total)
        repsPerRegion (float): number of total reps per region, based on
            seemingly arbitrary decision that the US, with 50 states, should
            have 435 representatives, just 'cuz
        baseline (int): number of reps each state gets before we move to
            proportional allotment

    returns:
        df (pandas.DataFrame): a copy of the input dataframe df with the
            targetColname column calculated and appended

    raises:
        NA

    """
    x = df.copy()

    # create region dataframe with baseline reps
    regions = x[[regionColname]].copy()
    regions.loc[:, 'baseline'] = baseline

    numRegions = len(regions)
    totReps = round(repsPerRegion * numRegions)
    preAllocated = regions.baseline.sum()
    toAllocate = totReps - preAllocated

    x = get_priority_values(x, N=toAllocate, popColname=popColname)

    # sort and truncate
    x = x.sort_values(by='priority_value', ascending=False)
    x = x.head(toAllocate)

    # aggregate for counts
    x = x[regionColname].value_counts().reset_index()
    x.columns = [regionColname, 'apportioned_reps']

    # join apportioned and baseline votes and return the result
    x = x.merge(regions, how='outer', on=regionColname)
    x.apportioned_reps.fillna(0, inplace=True)
    x.loc[:, targetColname] = x.apportioned_reps + x.baseline

    return x[[regionColname, targetColname]]


def get_priority_values(df, N, popColname='population'):
    # multipliers
    mults = pd.DataFrame(
        data=[(i * (i - 1)) ** -0.5 for i in range(2, N + 1)],
        columns=['multiplier']
    )

    # join to get state pop * multipliers
    df.loc[:, 'prodkey'] = 0
    mults.loc[:, 'prodkey'] = 0
    df = df.merge(mults, on='prodkey')
    df.loc[:, 'priority_value'] = df[popColname] * df.multiplier

    return df


def us_analyze():
    baseline = 1

    us = get_us()

    x = us.copy()

    # create region dataframe with baseline reps
    regions = x[['state']].copy()
    regions.loc[:, 'baseline'] = baseline

    numRegions = len(regions)
    totReps = round(RPR * numRegions)
    preAllocated = regions.baseline.sum()
    toAllocate = totReps - preAllocated

    x = get_priority_values(x, N=toAllocate, popColname='population')
    x = x.sort_values(by='priority_value', ascending=False)

    return x


def get_us():
    # load us
    us = pd.read_csv(FUS)
    us.population = us.population.str.replace(',', '').astype(int)

    # final row is a total row; drop it
    us = us.iloc[:-1, :]

    return us


def test():
    us = get_us()

    # calculate based on population column
    evs = num_reps(df=us[['state', 'population']])

    # assert equality
    x = us[['state', 'num_reps']].merge(evs, on='state', suffixes=('', '_1'))

    assert (x.num_reps == x.num_reps_1).all()
