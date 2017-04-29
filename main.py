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

def main(fRes=FRES, fPop=FPOP):
    """docstring

    args:

    returns:

    raises:

    """
    results = pd.read_csv(fRes, delimiter='\t')
    results.columns = [_.lower() for _ in results.columns]
    results = results[['department', 'em_votes', 'mlp_votes']]
    results.loc[:, 'em_wins'] = results.em_votes > results.mlp_votes

    population = pd.read_csv(fPop, delimiter='\t')
    population = population[['Department', 'Legal Population in 2013']]
    population.columns = ['department', 'population']

    # assign electoral votes based on population

    # join the two

    return results, population



if __name__ == '__main__':

    args = parse_args()

    main()
