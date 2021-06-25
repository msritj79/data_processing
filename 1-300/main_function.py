#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import openpyxl as px
import os
import glob
from natsort import natsorted
import time
from data_processing_model import DataProcessingModel

def main():

    # 実行するフォルダの選択 要記入！！！！！！！！！！！！！！！！！！！！！
    dir_list = ['bk7-dimple-3']
    for dir in dir_list:

        #finding csv files in the directry
        csv_path_list = natsorted(glob.glob(f'C:/Users/a0164006/Desktop/experiment_data/*/{dir}/*.csv'))

        #setting rotational speed
        rotation_speed_list = []
        legend_list = []

        for i in range(1, len(csv_path_list)+1):
            if i!=2:
                rotation_speed = np.array([1,3,10,50,100,300])
                legend_label = str(i) + "(1→300)"

            else:
                rotation_speed = np.array([300,100,50,10,3,1])
                legend_label = str(i) + "(300→1)"

            rotation_speed_list.append(rotation_speed)
            legend_list.append(legend_label)

        legend_list = ["2(300→1)", "3(1→300)", "7(1→300)", "8(1→300)", "9(1→300)"]
        #legend_list = ["dimple2", "dimple5", "dimple10", "nontex"]
        print(csv_path_list)

        model = DataProcessingModel(dir, csv_path_list, rotation_speed_list, legend_list)

        t1 = time.time()
        model.create_matrix()
        t2 = time.time()
        print("cre_mat:",(t2-t1))

        model.calculation()
        t3 = time.time()
        print("calc:",(t3-t2))

        model.create_graph()
        t4 = time.time()
        print("cre_graph:",(t4-t3))

        # create_excel(all_data_mat, mean_frition_mat, excel_path, len(csv_path_list), legend_list)
        # t5 = time.time()
        # print("cre_exe:",(t5-t4))


if __name__ == '__main__':
    main()
    print('END')