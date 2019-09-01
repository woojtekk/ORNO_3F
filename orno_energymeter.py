#!/usr/bin/env python
# encoding: utf-8
import os
import csv
import sys
import random
import struct
import operator
import pandas as pd
import energymeter
import datetime
# from old import energymeter


class orno:

    table2={
        "DateTime":                    [0,     0],
        "Grid Freq.":                  [0x3c,  2],
        "Grid Freq.":                  [0x14,  2],
        "Current L1":                  [0x16,  2],
        "Current L2":                  [0x18,  2],
        "Current L3":                  [0x1A,  2],
        "Active Power Total:":         [0x1C,  2],
        "Active Power L1:":            [0x1E,  2],
        "Active Power L2:":            [0x20,  2],
        "Active Power L3:":            [0x22,  2],
        "Total Active Energy TT":      [0x100,  2],
        "Total Active Energy T1":      [0x130,  2],
        "Total Active Energy T2":      [0x13C,  2],
        "Total Active Energy T3":      [0x148,  2],
        "Total reactive p.":           [36,  2]}

    def __init__(self):
        # if energymeter.testPort("/dev/ttyUSB0", 1):
        #     self.dev= energymeter.startClient("/dev/ttyUSB0", 1)
        # else:
        #     print("Some problems with device.... [EXIT]")
        #     sys.exit()
        #
        self.data_new=pd.DataFrame()
        
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

        if not os.path.isfile("/home/pi/ORNO_3F/data.txt"):
            print("DATA file not exist ..... creating new: data.txt")
            oo=pd.DataFrame.from_dict(self.table2)
            oo=oo.iloc[0:0]
            #oo[self.header_order].to_csv("data.txt", sep='\t',compression="gzip")
            oo[self.header_order].to_csv("/home/pi/ORNO_3F/data.txt", sep='\t')

    def update_data_file(self):
        #data_old = pd.read_csv('data.txt', index_col=0, sep='\t', compression="gzip")
        data_old = pd.read_csv('/home/pi/ORNO_3F/data.txt', index_col=0, sep='\t')
        data_to_save = data_old.append(self.data_new, sort=True)
        data_to_save = data_to_save.reset_index(drop=True)
        #data_to_save[self.header_order].to_csv("data.txt", sep='\t', compression="gzip")
        data_to_save[self.header_order].to_csv("/home/pi/ORNO_3F/data.txt", sep='\t')

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
        mbcli = energymeter.startClient("/dev/ttyUSB0", 1)
        now = datetime.datetime.now()

        qq=pd.DataFrame.from_dict(self.table2)
        for x in qq:
            if x == "DateTime":
                self.data_new[x] = now.strftime("%Y-%m-%d %H:%M")
            if qq[x][1] == 2 :
                regs = energymeter.readRegs(mbcli, qq[x][0], 2)
                self.data_new[x] = [round(self.mem2float(regs[0], regs[1]), 3)]
		txt=str(x)+"    \t  "+str(round(self.mem2float(regs[0], regs[1]),3))
		print(txt)



    def mem2float(self,reg1, reg2):
        # found on beloved "satckoverflow"
        raw = struct.pack('>HH', reg1, reg2)
        return struct.unpack('>f', raw)[0]

    def float2mem(self,flo):
        # found on beloved "satckoverflow"
        raw = struct.pack('>f', flo)
        regsy=struct.unpack('>HH', raw)
        return [regsy[0], regsy[1]]



if __name__ == "__main__":
    or3f=orno()
    print("koniec")
