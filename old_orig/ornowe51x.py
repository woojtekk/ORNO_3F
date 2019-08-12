#!/usr/bin/env python
# encoding: utf-8

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# Copyright (C) 2017 Piotr Murawski
# Niniejszy program jest wolnym oprogramowaniem; mozesz go
# rozprowadzac dalej i/lub modyfikowac na warunkach Powszechnej
# Licencji Publicznej GNU, wydanej przez Fundacje Wolnego
# Oprogramowania - wedlug wersji 3-ciej tej Licencji lub ktorejs
# z pozniejszych wersji.
# Niniejszy program rozpowszechniany jest z nadzieja iz bedzie on
# uzyteczny - jednak BEZ JAKIEJKOLWIEK GWARANCJI, nawet domyslnej
# gwarancji PRZYDATNOSCI HANDLOWEJ albo PRZYDATNOSCI DO OKRESLONYCH
# ZASTOSOWAN. W celu uzyskania blizszych informacji - Powszechna
# Licencja Publiczna GNU.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# Z pewnoscia wraz z niniejszym programem otrzymales tez egzemplarz
# Powszechnej Licencji Publicznej GNU (GNU General Public License);
# jesli nie - napisz do Free Software Foundation, Inc., 675 Mass Ave,
# Cambridge, MA 02139, USA.
# Powszechna Licencja GNU dostepna jest rowniez na stronie:
# http://www.gnu.org/licenses/licenses.html
# nieoficjalne polskie tlumaczenie na
# http://www.gnu.org.pl
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


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








