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

class DataProcessingStribeckModel:
    def __init__(self, dir_name, csv_path_list, bearing_num_mat, legend_list):

        #finding csv files in the directry
        self.csv_path_list = csv_path_list

        #setting save path
        result_dir_path = os.path.dirname(self.csv_path_list[0]).replace('experiment_data','experiment_result')
        self.excel_path = result_dir_path+'/'+dir_name+'_stribeck.xlsx'
        self.fig2_path = result_dir_path+'/'+dir_name+'_stribeck'
        self.fig3_path = result_dir_path+'/'+dir_name+'_stribeck_modified'

        #delete excel file if any exists
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)

        #create directry if not exist
        os.makedirs(result_dir_path, exist_ok=True)

        #setting rotational speed
        self.legend_list = legend_list
        self.bearing_num_mat = bearing_num_mat


    def create_matrix(self):

        self.all_data_mat = np.zeros((len(self.csv_path_list), 50000, 5))
        self.mean_friction_mat = np.zeros((len(self.csv_path_list), 6))

        i = -1                  #repetition number - 1
        for file_path in self.csv_path_list:

            i += 1

            col_names = ['c{:02d}'.format(i) for i in range(5)]
            df_csv = pd.read_csv(file_path, encoding='shift-jis', names=col_names)

            #recreate dataframe
            df_csv = df_csv.iloc[16:,1:3]

            #str→float
            df_csv = df_csv.astype(float)

            load = df_csv.iloc[1000,0]

            #start time(motor start) and finish time
            start_row = df_csv[df_csv.iloc[:,1] > 2.0].index[0]
            finish_row = len(df_csv)

            #finish time(load was reduced)
            if  df_csv.iloc[-1,0] < load-300:
                finish_row = df_csv[df_csv.iloc[:,0] < load-300].index[-1]

            #recreate dataframe
            df_csv = df_csv.iloc[start_row:finish_row,:]

            self.all_data_mat[i, :len(df_csv), 1:3] = df_csv.to_numpy()
            self.all_data_mat[i, :len(df_csv), 0] = range(len(df_csv))


    def calculation(self):
        #setting parameter
        r1 = 8.0        #inner radius[mm]
        r2 = 2.5        #outer radius[mm]
        l = 20          #load cell position[mm]
        g = 9.807
        pi = 3.142
        S = pi*(r1**2-r2**2)
        a = r1**3-r2**3
        sampling_freq = 50

        #calculation
        self.all_data_mat[:,:,0] = self.all_data_mat[:,:,0]/sampling_freq/60    #time[min]
        self.all_data_mat[:,:,3] = self.all_data_mat[:,:,1]*10**(-3)*g/S        #surface pressure[MPa]
        self.all_data_mat[:,:,4] = self.all_data_mat[:,:,2]*g*l*1.5/pi/self.all_data_mat[:,:,3]/a*10**(-3)  #friction coefficient

        #mean friction coefficient for each rotational speed
        min2 = int(2*60*sampling_freq)
        min3 = int(3*60*sampling_freq)
        min0 = int(min2/10)

        self.mean_friction_mat[:,0] = np.mean(self.all_data_mat[:, min3+min0:min3+min2, 4], axis=1)
        self.mean_friction_mat[:,1] = np.mean(self.all_data_mat[:, min3+min2+min0:min3+min2*2, 4], axis=1)
        self.mean_friction_mat[:,2] = np.mean(self.all_data_mat[:, min3+min2*2+min0:min3+min2*3, 4], axis=1)
        self.mean_friction_mat[:,3] = np.mean(self.all_data_mat[:, min3+min2*3+min0:min3+min2*4, 4], axis=1)
        self.mean_friction_mat[:,4] = np.mean(self.all_data_mat[:, min3+min2*4+min0:min3+min2*5, 4], axis=1)
        self.mean_friction_mat[:,5] = np.mean(self.all_data_mat[:, min3+min2*5+min0:min3+min2*6-100, 4], axis=1)


    def create_graph(self):
        #fig1(ax0,ax1):result for each repetetion num
        #fig2(ax2)    :total result
        #fig3(ax3)    :total result (with fixed y label)

        #creating fig2,3
        fig2 = plt.figure(figsize=(6,4))
        plt.rcParams['font.size'] = 26
        ax2 = fig2.add_subplot(1,1,1)
        fig3 = plt.figure(figsize=(6,4))
        plt.rcParams['font.size'] = 26
        ax3 = fig3.add_subplot(1,1,1)

        i=-1
        for csv_path in self.csv_path_list:

            i+=1
            # fig1_path = os.path.splitext(csv_path)[0].replace('experiment_data','experiment_result')

            # #axis value
            # time = self.all_data_mat[i,:,0]
            surf_pre = self.all_data_mat[i,:,3]
            # fri_coef = self.all_data_mat[i,:,4]
            mean_fri_coef = self.mean_friction_mat[i,:]

            pm = np.mean(surf_pre)*10**6      #mean surface pressure
            bearing_num_mat = self.bearing_num_mat / pm

            x_all = np.linspace(bearing_num_mat[0,0], bearing_num_mat[0,-1], 100)


            # #fig1
            # fig1 = plt.figure(figsize=(6,10))
            # plt.rcParams['font.size'] = 20
            # ax0 = fig1.add_subplot(2,1,1)
            # ax1 = fig1.add_subplot(2,1,2)
            # ax0.plot(time, fri_coef)
            # ax1.plot(time, fri_coef)

            # #range of label
            # min_t = 0
            # max_t = 15
            # min_y2 = 0
            # max_y2 = 0.2

            # ax0.set_xlim(min_t, max_t)
            # ax0.set_ylim(min_y2, max_y2)
            # ax1.set_xlim(min_t, max_t)

            # #title, label
            # #ax0.set_title('friction coefficient - time')
            # ax0.set_xlabel('time (min)')
            # ax0.set_ylabel('friction coefficient')
            # #ax1.set_title('friction coefficient - rotation speed')
            # ax1.set_xlabel('time (min)')
            # ax1.set_ylabel('friction coefficient')

            # #space between graphs
            # fig1.subplots_adjust(hspace=0.4,wspace=0.5)
            # fig1.subplots_adjust(wspace=1)

            # #saving fig1
            # fig1.savefig(fig1_path,bbox_inches='tight')

            #fig2
            ax2.plot(bearing_num_mat[i], mean_fri_coef, marker='o', label=self.legend_list[i])
            ax2.legend(bbox_to_anchor=(1.01,1), loc='upper left', borderaxespad=0, fontsize=22)
            #ax2.set_title('friction coefficient - rotation speed',fontsize=17)
            ax2.set_xlabel('bearing characteristic number (ηN/p)')
            ax2.set_ylabel('friction coefficient')
            ax2.set_xscale('log')

            #fig3
            ax3.plot(bearing_num_mat[i], mean_fri_coef, marker='o', label=self.legend_list[i])
            ax3.legend(bbox_to_anchor=(1.01,1), loc='upper left', borderaxespad=0, fontsize=22)
            #ax3.set_title('friction coefficient - rotation speed',fontsize=17)
            ax3.set_xlabel('bearing characteristic number (ηN/p)')
            ax3.set_ylabel('friction coefficient')
            ax3.set_yticks(np.arange(0, 0.31, 0.1))
            ax3.set_xscale('log')

        fig2.savefig(self.fig2_path,bbox_inches='tight')
        fig3.savefig(self.fig3_path,bbox_inches='tight')

        plt.close()


    def create_excel(self):

        repetition_num = len(self.csv_path_list)
        for i in range(repetition_num):

            sheetname = 'number of times_' + str(i+1)

            fin_row = int(np.where(self.all_data_mat[i,:,0]<0.0001)[0][1])
            all_data_mat_i = self.all_data_mat[i,:fin_row,:]

            df_i = pd.DataFrame(all_data_mat_i)
            df_i.columns = ['time[min]','load[g]','friction force[g]','surface pressure[MPa]','friction coefficient']

            if os.path.exists(self.excel_path):
                with pd.ExcelWriter(self.excel_path,mode='a') as writer:
                    df_i.to_excel(writer, sheet_name=sheetname)

            else:
                with pd.ExcelWriter(self.excel_path) as writer:
                    df_i.to_excel(writer, sheet_name=sheetname)

        df_mean_fri = pd.DataFrame(np.zeros((8,repetition_num+1)))
        df_mean_fri.iloc[0,:2] = ['time[min]','mean friction coefficient']
        df_mean_fri.iloc[1,1:] = self.legend_list
        df_mean_fri.iloc[2:,0] = ['3-5','5-7','7-9','9-11','11-13','13-15']
        df_mean_fri.iloc[2:,1:] = self.mean_friction_mat.T
        df_mean_fri[df_mean_fri==0] = None

        with pd.ExcelWriter(self.excel_path,mode='a') as writer:
                    df_mean_fri.to_excel(writer, sheet_name='mean_friction_coefficient')