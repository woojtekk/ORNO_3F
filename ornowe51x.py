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

import crc16
import sys
import os
import energymeter
import math
import struct
import datetime
DEVICE_0="/dev/ttyUSB0"
ADDR=1
table=(
0x000, 0x002, 0x003, 0x004,
0x006, 0x009, 0x00B, 0x00D,
0x00E, 0x010, 0x012, 0x014,
0x016, 0x018, 0x01A, 0x01C,
0x01E, 0x020, 0x022, 0x024,
0x026, 0x028, 0x02A, 0x02C,
0x02E, 0x030, 0x032,
0x034, 0x036, 0x038, 0x03A,
0x03C, 0x041, 0x100, 0x102,
0x104, 0x106, 0x108, 0x10A,
0x10C, 0x10E, 0x110, 0x112,
0x114, 0x116, 0x118, 0x11A,
0x11C, 0x11E, 0x120, 0x122,
0x124, 0x126, 0x128, 0x12A,
0x12C, 0x12E, 0x130, 0x132,
0x134, 0x136, 0x138, 0x13A,
0x13C, 0x13E, 0x140, 0x142,
0x144, 0x146, 0x148, 0x14A,
0x14C, 0x14E, 0x150, 0x152,
0x154, 0x156, 0x158, 0x15A,
0x15C, 0x15E)


def mem2float(reg1, reg2):
    # found on beloved "satckoverflow"
    raw = struct.pack('>HH', reg1, reg2)
    return struct.unpack('>f', raw)[0]

def float2mem(flo):
    # found on beloved "satckoverflow"
    raw = struct.pack('>f', flo)
    regsy=struct.unpack('>HH', raw)
    return [regsy[0], regsy[1]]



testEmeter=energymeter.testPort(DEVICE_0, ADDR)
if testEmeter:
   mbcli = energymeter.startClient(DEVICE_0, ADDR)

   regs_t0=energymeter.readRegs(mbcli, 0x100,2)
   regs_t1=energymeter.readRegs(mbcli, 0x130,2)
   regs_t2=energymeter.readRegs(mbcli, 0x13C,2)


   txt =str(datetime.datetime.now())
   txt+=" Total: "+ str( mem2float(regs_t0[0],regs_t0[1]))
   txt+=" T1: "+ str( mem2float(regs_t1[0],regs_t1[1]))
   txt+=" T2: "+ str( mem2float(regs_t2[0],regs_t2[1]))+"\n"

   print txt

   with open('/home/pi/ORNO_3F/energy.log', 'a') as file:
      file.write(txt)


   xold=-2
   for x in table:
	dx= x-xold
	xold=x
	regs=energymeter.readRegs(mbcli, x,dx)
	print x, " :: ", round(mem2float(regs[0],regs[1]),3)


else:

   print "ERROR: meter not found"
