#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: main.py
Author: zlamberty
Created: 2017-04-28

Description:


Usage:
    <usage>

"""

import os

import pandas as pd

import representatives


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

HERE = os.path.realpath(os.path.dirname(__file__))
DATA = os.path.join(HERE, 'data')
FRES = os.path.join(DATA, 'results.tsv')
FPOP = os.path.join(DATA, 'population.tsv')


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def load_results(fres=FRES):
    """load french runoff election results and determine which candidate won
    each department

    """
    results = pd.read_csv(fres, delimiter='\t')
    results.columns = [c.lower() for c in results.columns]
    pcts = [c for c in results.columns if '_pct' in c]
    results = results.set_index('department')[pcts]
    results.loc[:, "winner"] = results.idxmax(axis=1).str.extract(
        '(\w+)_pct', expand=False
    )
    return results


def load_population(fpop=FPOP):
    population = pd.read_csv(fpop, delimiter='\t')
    population = population[['Department', 'Legal Population in 2013']]
    population.columns = ['department', 'population']
    return population


def main(fres=FRES, fpop=FPOP):
    """docstring

    args:

    returns:

    raises:

    """
    results = load_results(fres)

    print('\nfirst round results ---------------------------------------------')
    print(results.loc['Total', :])

    results = results.drop('Total')
    results = results.reset_index()

    population = load_population(fpop)

    # assign electoral vote numbers based on population
    population.loc[:, 'num_sen'] = 2

    reps = representatives.num_reps(
        population[['department', 'population']], regionColname='department'
    )

    population = population.merge(reps, on='department')

    population.loc[:, 'evs'] = population.num_sen + population.num_reps

    # join the two and return
    return population.merge(results, on='department')


if __name__ == '__main__':
    x = main()

    print('\nelectoral vote totals -------------------------------------------')
    print(x.groupby('winner').evs.sum())

    print('\nelectoral vote percentages --------------------------------------')
    print(x.groupby('winner').evs.sum() / x.evs.sum())
