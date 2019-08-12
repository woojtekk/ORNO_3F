#!/usr/bin/env python
# encoding: utf-8


import sys
import os
import energymeter
import math
import struct

DEVICE_0="/dev/ttyUSB0"
ADDR=1


def mem2float(reg1, reg2):
    # found on beloved "satckoverflow"
    raw = struct.pack('>HH', reg1, reg2)
    return struct.unpack('>f', raw)[0]

def float2mem(flo):
    # found on beloved "satckoverflow"
    raw = struct.pack('>f', flo)
    regsy=struct.unpack('>HH', raw)
    return [regsy[0], regsy[1]]



print "testing @ ",DEVICE_0
testEmeter=energymeter.testPort(DEVICE_0, ADDR)
if testEmeter:
   print "meter ok"
   mbcli = energymeter.startClient(DEVICE_0, ADDR)
   #print regs

   regs=energymeter.readRegs(mbcli, 60,5)
   print regs
   print " ... ", round(mem2float(regs[0],regs[1]),2)
   print " ... ", round(mem2float(regs[2],regs[3]),2)

   regs=energymeter.readRegs(mbcli, 0xE,6)
   print regs
   print "volatge L1 ... ", round(mem2float(regs[0], regs[1]),1)
   print "volatge L2 ... ", round(mem2float(regs[2], regs[3]),1)
   print "volatge L3 ... ", round(mem2float(regs[4], regs[5]),1)
   regs=energymeter.readRegs(mbcli, 0x16,6)
   print
   print "current L1 ... ", round(mem2float(regs[0], regs[1]),2)
   print "current L2 ... ", round(mem2float(regs[2], regs[3]),2)
   print "current L3 ... ", round(mem2float(regs[4], regs[5]),2)
   regs=energymeter.readRegs(mbcli, 0x1C,8)
   print
   print "power total .. ", round(mem2float(regs[0], regs[1]),3)
   print "power   L1 ... ", round(mem2float(regs[2], regs[3]),3)
   print "power   L2 ... ", round(mem2float(regs[4], regs[5]),3)
   print "power   L3 ... ", round(mem2float(regs[6], regs[7]),3)
   regs=energymeter.readRegs(mbcli, 0x100,8)
   print
   print "energy total.. ", round(mem2float(regs[0], regs[1]),3)
   print "energy  L1 ... ", round(mem2float(regs[2], regs[3]),3)
   print "energy  L2 ... ", round(mem2float(regs[4], regs[5]),3)
   print "energy  L3 ... ", round(mem2float(regs[6], regs[7]),3)
   regs=energymeter.readRegs(mbcli, 0x14,2)
   print
   print "net frequency. ", round(mem2float(regs[0], regs[1]),4)


   #print energymeter.writeRegs(mbcli, 0x9, float2mem(12000))



else:

   print "ERROR: meter not found"








