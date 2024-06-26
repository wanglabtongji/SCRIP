#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   calculation.py
@Time    :   2021/04/16 12:35:01
@Author  :   Xin Dong
@Contact :   xindong9511@gmail.com
@License :   (C)Copyright 2020-2021, XinDong
'''

import sys
import numpy as np
import pandas as pd
from sklearn import preprocessing
from SCRIP.utilities.utils import excute_info


def standardScaler(t):
    scaler = preprocessing.StandardScaler().fit(t)
    rt = pd.DataFrame(scaler.transform(t), index=t.index, columns=t.columns)
    return rt


@excute_info('Summary result from dataset level to factor level.')
def map_factor_on_ChIP(table, mode):
    ret_table = table.copy()
    # map factor by id "_"
    factor_index_list = []
    for i in ret_table.index:
        factor_name = i.split("_")
        factor_index_list.append(factor_name[0])
    ret_table.loc[:, "Factor"] = factor_index_list
    if mode == 'max':
        factor_table = ret_table.groupby("Factor").max()
    elif mode == 'mean':
        factor_table = ret_table.groupby("Factor").mean()
    else:
        sys.exit(205)
    return factor_table

@excute_info('Getting the best reference for each cell.')
def get_factor_source(table):
    ret_table = table.copy()
    # map factor by id "_"
    factor_index_list = []
    for i in ret_table.index:
        factor_name = i.split("_")
        factor_index_list.append(factor_name[0])
    ret_table.loc[:, "Factor"] = factor_index_list
    max_index = ret_table.groupby("Factor").idxmax()
    return max_index


def cal_score(dataset_overlap_df, peaks_number, qpeak_length):
    '''
    nql: normalize query peak length
    dm: minus the mean
    '''
    dataset_cell_percent = (dataset_overlap_df.T/peaks_number.loc[dataset_overlap_df.index, 1]).T
    dataset_cell_percent_dl = dataset_cell_percent/qpeak_length.loc[dataset_cell_percent.columns, 1]
    dataset_cell_percent_dl_dm = (dataset_cell_percent_dl.T - dataset_cell_percent_dl.mean(1)).T
    # dataset_cell_percent_scale = (dataset_cell_percent/dataset_cell_percent.sum())*1e4
    # dataset_cell_percent_scale_dm = (dataset_cell_percent_scale.T/dataset_cell_percent_scale.mean(1)).T
    return dataset_cell_percent_dl_dm


def score_normalization(dataset_cell_df, mode):
    tf_cell_df = map_factor_on_ChIP(dataset_cell_df, mode)
    tmp = standardScaler(tf_cell_df.T).T
    tf_cell_df_lsn = 1/(1+np.exp(-tmp))  # LSN(Logistic Sigmoid Normalisation)
    tf_cell_df_lsn_std = standardScaler(tf_cell_df_lsn)
    return tf_cell_df_lsn_std
