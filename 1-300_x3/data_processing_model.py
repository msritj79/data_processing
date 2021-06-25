#!/usr/bin/env python
# coding: utf-8

from posixpath import split
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl as px
import os

class DataProcessingModel:
    def __init__(self, dir_name, csv_path, rotation_speed_list, legend_list):

        #finding csv files in the directry
        self.csv_path = csv_path

        #setting save path
        result_dir_path = os.path.dirname(self.csv_path).replace('experiment_data','experiment_result')
        self.excel_path = result_dir_path+'/'+dir_name+'.xlsx'
        self.fig2_path = result_dir_path+'/'+dir_name+'_all_results'
        self.fig3_path = result_dir_path+'/'+dir_name+'_all_results_modified'

        #delete excel file if any exists
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)

        #create directry if not exist
        os.makedirs(result_dir_path, exist_ok=True)

        #setting rotational speed
        self.rot_list = rotation_speed_list
        self.legend_list = legend_list


    def create_matrix(self):

        col_names = ['c{:02d}'.format(i) for i in range(5)]
        df_csv = pd.read_csv(self.csv_path, encoding='shift-jis', names=col_names)

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

        sampling_freq = 50
        min15 = 15*60*sampling_freq
        min10 = 10*60*sampling_freq

        split_arr = [start_row, start_row+min15, start_row+min15+min10, start_row+min15+min10*2,
                    start_row+min15+min10*3, start_row+min15+min10*4, start_row+min15+min10*5]  #after first 15min, split data each 10min
        csv_mat = df_csv.to_numpy()
        csv_mat_list = np.split(csv_mat, split_arr)

        self.all_data_mat = np.zeros((6, min15, 5))
        self.mean_friction_mat = np.zeros((6, 6))

        self.all_data_mat[0, :min15, 1:3] = csv_mat_list[1]
        self.all_data_mat[1, :min10, 1:3] = csv_mat_list[2]
        self.all_data_mat[2, :min10, 1:3] = csv_mat_list[3]
        self.all_data_mat[3, :min10, 1:3] = csv_mat_list[4]
        self.all_data_mat[4, :min10, 1:3] = csv_mat_list[5]
        self.all_data_mat[5, :len(csv_mat_list[6]), 1:3] = csv_mat_list[6]

        self.all_data_mat[0, :min15, 0] = range(min15)
        self.all_data_mat[1, :min15, 0] = range(min15)
        self.all_data_mat[2, :min15, 0] = range(min15)
        self.all_data_mat[3, :min15, 0] = range(min15)
        self.all_data_mat[4, :min15, 0] = range(min15)
        self.all_data_mat[5, :min15, 0] = range(min15)


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

        self.mean_friction_mat[0,0] = np.mean(self.all_data_mat[0, min3+min0:min3+min2, 4])
        self.mean_friction_mat[0,1] = np.mean(self.all_data_mat[0, min3+min2+min0:min3+min2*2, 4])
        self.mean_friction_mat[0,2] = np.mean(self.all_data_mat[0, min3+min2*2+min0:min3+min2*3, 4])
        self.mean_friction_mat[0,3] = np.mean(self.all_data_mat[0, min3+min2*3+min0:min3+min2*4, 4])
        self.mean_friction_mat[0,4] = np.mean(self.all_data_mat[0, min3+min2*4+min0:min3+min2*5, 4])
        self.mean_friction_mat[0,5] = np.mean(self.all_data_mat[0, min3+min2*5+min0:min3+min2*6-100, 4])

        self.mean_friction_mat[1:,1] = np.mean(self.all_data_mat[1:, min0:min2, 4], axis=1)
        self.mean_friction_mat[1:,2] = np.mean(self.all_data_mat[1:, min2+min0:min2*2, 4], axis=1)
        self.mean_friction_mat[1:,3] = np.mean(self.all_data_mat[1:, min2*2+min0:min2*3, 4], axis=1)
        self.mean_friction_mat[1:,4] = np.mean(self.all_data_mat[1:, min2*3+min0:min2*4, 4], axis=1)
        self.mean_friction_mat[1:,5] = np.mean(self.all_data_mat[1:, min2*4+min0:min2*5-500, 4], axis=1)

        self.mean_friction_mat[1,0] = self.mean_friction_mat[0,5]
        self.mean_friction_mat[2,0] = self.mean_friction_mat[1,5]
        self.mean_friction_mat[3,0] = self.mean_friction_mat[2,5]
        self.mean_friction_mat[4,0] = self.mean_friction_mat[3,5]
        self.mean_friction_mat[5,0] = self.mean_friction_mat[4,5]
        print(self.mean_friction_mat)

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

        for i in range(len(self.all_data_mat)):

            fig1_path = os.path.splitext(self.csv_path)[0].replace('experiment_data','experiment_result')+'_'+ str(i+1)

            #axis value
            time = self.all_data_mat[i,:,0]
            surf_pre = self.all_data_mat[i,:,3]
            fri_coef = self.all_data_mat[i,:,4]
            mean_fri_coef = self.mean_friction_mat[i,:]


            #fig1
            fig1 = plt.figure(figsize=(6,10))
            plt.rcParams['font.size'] = 20
            ax0 = fig1.add_subplot(2,1,1)
            ax1 = fig1.add_subplot(2,1,2)
            ax0.plot(time, fri_coef)
            ax1.plot(time, fri_coef)

            #range of label
            min_t = 0
            max_t = 15
            min_y2 = 0
            max_y2 = 0.2

            ax0.set_xlim(min_t, max_t)
            ax0.set_ylim(min_y2, max_y2)
            ax1.set_xlim(min_t, max_t)

            #title, label
            #ax0.set_title('friction coefficient - time')
            ax0.set_xlabel('time (min)')
            ax0.set_ylabel('friction coefficient')
            #ax1.set_title('friction coefficient - rotation speed')
            ax1.set_xlabel('time (min)')
            ax1.set_ylabel('friction coefficient')

            #space between graphs
            fig1.subplots_adjust(hspace=0.4,wspace=0.5)
            fig1.subplots_adjust(wspace=1)
            
            #saving fig1
            fig1.savefig(fig1_path,bbox_inches='tight')

            #fig2
            ax2.plot(self.rot_list[i], mean_fri_coef, marker='o', label=self.legend_list[i])
            ax2.legend(bbox_to_anchor=(1.01,1), loc='upper left', borderaxespad=0, fontsize=22)
            #ax2.set_title('friction coefficient - rotation speed',fontsize=17)
            ax2.set_xlabel('rotation speed (rpm)')
            ax2.set_ylabel('friction coefficient')

            #fig3
            ax3.plot(self.rot_list[i], mean_fri_coef, marker='o', label=self.legend_list[i])
            ax3.legend(bbox_to_anchor=(1.01,1), loc='upper left', borderaxespad=0, fontsize=22)
            #ax3.set_title('friction coefficient - rotation speed',fontsize=17)
            ax3.set_xlabel('rotational speed (rpm)')
            ax3.set_ylabel('friction coefficient')
            ax3.set_yticks(np.arange(0, 0.31, 0.1))
            
        fig2.savefig(self.fig2_path,bbox_inches='tight')
        fig3.savefig(self.fig3_path,bbox_inches='tight')

        plt.close()


###################mistake##################333
    def create_excel(self):

        repetition_num = len(self.csv_path)
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