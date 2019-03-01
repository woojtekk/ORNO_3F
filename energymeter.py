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

import serial
import time
import mbusbase
import mbusclient
from   mbusbase import bytestr
 

energyclient = None


def createClient(portDevice, adres):
	tecl = mbusclient.mbclientserial()
        tecl.adres = adres
	tecl.transportOpen(portDevice, brate=9600,parity=serial.PARITY_EVEN)
	return tecl
	try:
		pass
	except:
		print "ERROR: can't get modbus client to work!"
		pass
	return None
	

def readRegs(client, start, cnt):
	r03 = mbusbase.request03(client.adres, start, cnt)
        bytes=r03.rtu();
	client.transportSend(bytes)
	reply=client.getReply()
	if reply:
		if reply.fail:
			return None
		else:
			return reply.vals
	return None 				 			
	

def writeRegs(client, addr, regs):
	r16 = mbusbase.request16(client.adres,addr,regs)
        bytes=r16.rtu();
	client.transportSend(bytes)
	reply=client.getReply()
	if reply:
		if reply.fail:
			return None
		else:
			return reply.vals
	return None



def testPort(portDevice, adres):
	mbcli = createClient(portDevice, adres)
	if mbcli!=None:
		regs = readRegs(mbcli, 0x40, 1)
		mbcli.transportClose()
		if regs!=None:
			if len(regs)>=1:
				return True 
		
	return False  



def startClient(portDevice, adres):
	#print "Energy MODBUS: " + portDevice
	mbcli = createClient(portDevice, adres)
	if mbcli!=None:
		global energyclient
		energyclient = mbcli
                return mbcli


		
		
		
		
		
		
		
		
			
