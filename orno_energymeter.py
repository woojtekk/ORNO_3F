#!/usr/bin/env python3.5
# encoding: utf-8
#https://techsparx.com/energy-system/modbus/linux-modbus-usb-rs485.html
import os
import csv
import sys
import random
import signal
import shutil

import time
import operator
import pandas as pd
import energymeter
class orno:

    table2={
        "Serial_Number":            [0,   0],
        "Modbus ID":                [2,   2],
        "Modbus Baudrate":          [3,   1],
        "Software Ver.":            [4,   1],
        "Hardware Version":         [6,   2],
        "SO output rate":           [9,   3],
        "Combined Code":            [11,  2],
        "LCD Cycle Time":           [13,  2],
        "L1 Voltage":               [14,  1],
        "L2 Voltage":               [16,  2],
        "L3 Voltage":               [18,  2],
        "Grid Freq.":               [20,  2],
        "L1 Current":               [22,  2],
        "L2 Current":               [24,  2],
        "L3 Current":               [26,  2],
        "Total Active Power":       [28,  2],
        "L1 Active Power":          [30,  2],
        "L2 Active Power":          [32,  2],
        "L3 Active Power":          [34,  2],
        "Total reactive p.":        [36,  2],
        "L1 reactive power":        [38,  2],
        "L2 reactive power":        [40,  2],
        "L3 reactive power":        [42,  2],
        "Total apparent p.":        [44,  2],
        "L1 apparent power":        [46,  2],
        "L2 apparent power":        [48,  2],
        "L3 apparent power":        [50,  2],
        "Total Power Factor":       [52,  2],
        "L1 power factor":          [54,  2],
        "L2 power factor":          [56,  2],
        "L3 power factor":          [58,  2],
        "Date Time":                [60,  2],
        "CRC code":                 [65,  5],
        "end":                      [160, 95],
        "Total Active Energy":      [256, 96],
        "L1 Active Energy":         [258, 2],
        "L2 Active Energy":         [260, 2],
        "L3 Active Energy":         [262, 2],
        "Total Forward Active Energy":  [264, 2],
        "L1 Forward Active Energy": [266, 2],
        "L2 Forward Active Energy": [268, 2],
        "L3 Forward Active Energy": [270, 2],
        "Total Reverse Energy":     [272, 2],
        "L1 Reverse Energy":        [274, 2],
        "L2 Reverse Energy":        [276, 2],
        "L3 Reverse Energy":        [278, 2],
        "Total Reactive Energy":    [280, 2],
        "L1 Reactive Energy":       [282, 2],
        "L2 Reactive Energy":       [284, 2],
        "L3 Reactive Energy":       [286, 2],
        "Total Forward Reactive Energy":    [288, 2],
        "L1 Forward Reactive Energy":       [290, 2],
        "L2 Forward Reactive Energy":       [292, 2],
        "L3 Forward Reactive Energy":       [294, 2],
        "Total Reverse Reactive Energy":    [296, 2],
        "L1 Reverse Reactive Energy":       [298, 2],
        "L2 Reverse Reactive Energy":       [300, 2],
        "L3 Reverse Reactive Energy":       [302, 2],
        "T1 Total Active Energy":           [304, 2],
        "T1 Total Forward Active Energy":   [306, 2],
        "T1 Total Reverse Active Energy":   [308, 2],
        "T1 Total Reactive Energy":         [310, 2],
        "T1 Total Forward Reactive Energy": [312, 2],
        "T1 Total Reverse Reactive Energy": [314, 2],
        "T2 Total Active Energy":           [316, 2],
        "T2 Total Forward Active Energy " : [318, 2],
        "T2 Total Reverse Active Energy " : [320, 2],
        "T2 Total Reactive Energy "       : [322, 2],
        "T2 Total Forward Reactive Energy": [324, 2],
        "T2 Total Reverse Reactive Energy": [326, 2],
        "T3 Total Active Energy "         : [328, 2],
        "T3 Total Forward Active Energy " : [330, 2],
        "T3 Total Reverse Active Energy " : [332, 2],
        "T3 Total Reactive Energy "       : [334, 2],
        "T3 Total Forward Reactive Energy": [336, 2],
        "T3 Total Reverse Reactive Energy": [338, 2],
        "T4 Total Active Energy "         : [340, 2],
        "T4 Total Forward Active Energy " : [342, 2],
        "T4 Total Reverse Active Energy " : [344, 2],
        "T4 Total Reactive Energy "       : [346, 2],
        "T4 Total Forward Reactive Energy": [348, 2],
        "T4 Total Reverse Reactive Energy": [350, 2]
    }

    def __init__(self):
        if energymeter.testPort("/dev/ttyUSB0", 1):
            self.dev=energymeter.startClient("/dev/ttyUSB0", 1)
        else:
            print("Some problems with device.... [EXIT]")
            sys.exit()
            
        
        self.check()
        self.read_all_channels()
        self.update_data_file()

    def __call__(self, *args, **kwargs):
        self.read_all_channels()
        self.update_data_file()
        return 0
    
    def check(self):
        self.header_order=[]
        for key, value in sorted(self.table2.items(), key=operator.itemgetter(1)):
             self.header_order.append(key)

        if not os.path.isfile("data.txt"):
            print("DATA file not exist ..... creating new")
            oo=pd.DataFrame.from_dict(self.table2)
            oo=oo.iloc[0:0]
            oo[self.header_order].to_csv("data.txt", sep='\t',compression="infer")
        
    def import_config(self):
        reader = csv.reader(open("dict.csv"))
        dic = {}
        remove=str.maketrans(dict.fromkeys('[,]'))
        for row in reader:
            a = row[1].translate(remove).split()
            dic[row[0]] = [int(a[0]),int(a[1])]
        self.chtoread = dic
        print(dic)

    def open_data_file():
        with open('dict.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in table.items():
                writer.writerow([key, value])
        return 0


    def read_all_channels(self):
        self.data_new=pd.DataFrame()

        qq=pd.DataFrame.from_dict(self.table2)
        for x in qq:
            self.data_new[x]=[round(round(random.uniform(0,0.9),4),3)]
            
    def update_data_file(self):
        data_old = pd.read_csv('data.txt', index_col=0, sep='\t',compression="infer")
        
        data_to_save = data_old.append(self.data_new,sort=True)
        data_to_save = data_to_save.reset_index(drop=True)
        
        data_to_save[self.header_order].to_csv("data.txt", sep='\t',compression="infer")

        


if __name__ == "__main__":
    or3f=orno()
    or3f("asd")
