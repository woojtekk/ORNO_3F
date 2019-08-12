#!/usr/bin/env python3.5
# encoding: utf-8
import os
import csv
import sys
import random
import struct
import operator
import pandas as pd
import energymeter
# from old import energymeter


class orno:

    table2={
        "L1 Voltage":               [14,  1],
        "L2 Voltage":               [16,  2],
        "L3 Voltage":               [18,  2],
        "Grid Freq.":               [20,  2],
        "L1 Current":               [22,  2],
        "L2 Current":               [24,  2],
        "L3 Current":               [26,  2],
        "Total Active Power":       [28,  2],
        "Total reactive p.":        [36,  2]}

    def __init__(self):
        # if energymeter.testPort("/dev/ttyUSB0", 1):
        #     self.dev= energymeter.startClient("/dev/ttyUSB0", 1)
        # else:
        #     print("Some problems with device.... [EXIT]")
        #     sys.exit()
        #
        
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
            print("DATA file not exist ..... creating new: data.txt")
            oo=pd.DataFrame.from_dict(self.table2)
            oo=oo.iloc[0:0]
            # oo[self.header_order].to_csv("data.txt", sep='\t',compression="None")
            oo[self.header_order].to_csv("data.txt", sep='\t')

    def update_data_file(self):
        # data_old = pd.read_csv('data.txt', index_col=0, sep='\t', compression="None")
        data_old = pd.read_csv('data.txt', index_col=0, sep='\t')
        data_to_save = data_old.append(self.data_new, sort=True)
        data_to_save = data_to_save.reset_index(drop=True)
        # data_to_save[self.header_order].to_csv("data.txt", sep='\t', compression="None")
        data_to_save[self.header_order].to_csv("data.txt", sep='\t')

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

        self.data_new=pd.DataFrame()

        qq=pd.DataFrame.from_dict(self.table2)
        for x in qq:
            if qq[x][1] == 2 :
                regs = energymeter.readRegs(mbcli, qq[x][0], 2)
                self.data_new[x] = round(self.mem2float(regs[0], regs[1]), 2)
                print((qq[x][0],round(self.mem2float(regs[0], regs[1]), 2),x))


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
    or3f("asd")
    print("koniec")
