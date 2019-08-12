#!/usr/bin/python

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



import time
import serial
import mbusbase
from   mbusbase import get16, get8, bytestr, errcode 
import socket
import sys


FAILCODE_SOCKET       = 1
FAILCODE_CONNECT      = 2
FAILCODE_NODATA       = 3
FAILCODE_TIMEOUT      = 4
FAILCODE_SOCKETSEND   = 5
FAILCODE_SOCKETREAD   = 6
FAILCODE_LENGTH       = 7
FAILCODE_SERIAL       = 8
FAILCODE_SERIALWRITE  = 9
FAILCODE_SERIALREAD   = 10
FAILCODE_TCPSEQUENCE  = 11

class MbclientFail(Exception):
    def __init__(self, message, code):
        super(MbclientFail, self).__init__(message)
        self.code = code



class mbclient(object):
	transportOpen=False
	TOUTMSG=1.0
	TOUTCHAR=6
	def __init__(self):
		pass	

	def getReply(self):
		bstr=self.transportRead(3,self.TOUTMSG)
		if bstr != '' and bstr!=None:
			if len(bstr)<3:
				raise MbclientFail("Not enough bytes received, <3",FAILCODE_NODATA)
			bajty=bytearray(bstr)
			#print bytestr(bajty)
			# find expected length
			bytescnt=0
			if bajty[1]==1 or bajty[1]==2:
				bytescnt = int(bajty[2])
			elif bajty[1]==3 or bajty[1]==4:
				bytescnt = int(bajty[2])
			elif bajty[1]==5:
				bytescnt = 4
			elif bajty[1]==5 or bajty[1]==6:
				bytescnt = 3
			elif bajty[1]==5 or bajty[1]==15 or  bajty[1]==16:
				bytescnt = 4
			elif bajty[1]>127:
				bytescnt = 0 
			bytescnt+=2
			#print 'Expected bytes : ' + str(bytescnt)
			bstr=self.transportRead(bytescnt,self.charTout * 256)
			#print 'bytes : ',len(bstr)
			if bstr != '':
				if len(bstr)<bytescnt:
					return None					 
				bajtydata=bytearray(bstr)
				#print bytestr(bajtydata)
				apdu=bajty+bajtydata
				rtu = mbusbase.receivedRtu(apdu)
				rtu.clientParse()
				return rtu
		else:
			raise MbclientFail("Receive timeout",FAILCODE_TIMEOUT)
		 
	
	def transportOpen(self):
		pass

	def transportClose(self):			
		return None

	def sendRequest(self, request):			
		return None
	
	def transportSend(self, rawbytes):			
		return None
	
	def transportRead(self, count,timeout=None):			
		return None


	def readCoils(self, adres, start, cnt):		
		self.sendRequest(mbusbase.request01(adres, start, cnt) )
		return self.awaitReply()

	def readInputs(self, adres, start, cnt):		
		self.sendRequest(mbusbase.request02(adres, start, cnt) )
		return self.awaitReply()
	
	def readInputRegs(self, adres, start, cnt):		
		self.sendRequest(mbusbase.request04(adres, start, cnt) )
		return self.awaitReply()

	def readHoldingRegs(self, adres, start, cnt):		
		self.sendRequest(mbusbase.request03(adres, start, cnt) )
		return self.awaitReply()
		
	def writeCoil(self, adres, addr, state):		
		self.sendRequest(mbusbase.request05(adres, addr, state) )
		return self.awaitReply()

	def writeCoils(self, adres, startaddr,coilsarr):		
		self.sendRequest(mbusbase.request15(adres, startaddr,coilsarr) )
		return self.awaitReply()

	def writeRegister(self, adres, addr, value):		
		self.sendRequest(mbusbase.request06(adres, addr, value) )
		return self.awaitReply()

	def writeRegisters(self, adres, startaddr,regarr):		
		self.sendRequest(mbusbase.request16(adres, startaddr,regarr) )
		return self.awaitReply()



class mbclienttcp(mbclient):
	portdev=None
	def transportOpen(self, clientAddress, timeout=0.9, port=502):
		self.clientAddress = clientAddress
		self.mainTout=timeout
		self.socke=None
		self.sequence=1
		self.port=port	
		self.charTout = timeout / 256
		self.lastsequence = 0 	
		serverAddress = (self.clientAddress, self.port)
		try:
			self.socke = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except Exception as inst:		
			raise MbclientFail("Can't open socket ["+inst.args[1]+']',FAILCODE_SOCKET)
		try:
			print >>sys.stderr, 'Connecting to %s:%s' % serverAddress
			self.socke.connect(serverAddress)			
		except Exception as inst:		
			raise MbclientFail("Can't connect socket @"+ str(self.clientAddress)+":"+str(self.port)+" ["+inst.args[1]+']',FAILCODE_CONNECT)
		
		self.transportOpen=True
	

	def transportClose(self):
		try:
			self.socke.close()
		except:
			pass
		return None
	
	
	def transportSend(self, rawbytes):
		if not self.transportOpen:
			return None
		try:
			self.socke.sendall(rawbytes)
			return
		except Exception as inst:
			raise MbclientFail("Socket send error ["+inst.args[1]+']',FAILCODE_SOCKETSEND)
		return None
	

	def transportRead(self, count, timeout):		
		self.socke.settimeout(timeout)
		if not self.transportOpen:
			return None
		try:
			return self.socke.recv(count, socket.MSG_WAITALL)
		except Exception as inst:
			raise MbclientFail("Socket read error ["+inst.args[1]+']',FAILCODE_SOCKETREAD)
		return None

	def sendRequest(self, request):		
		bytes=request.tcp(self.sequence)	
		self.lastsequence=self.sequence	
		self.sequence+=1						
		return self.transportSend(bytes)		


	def awaitReply(self):
		bstr=self.transportRead(6,self.TOUTMSG)			
		if len(bstr)!=6:
			raise MbclientFail("Not enough bytes received, <6 ",FAILCODE_NODATA)						
		else:
			bajty=bytearray(bstr)
			#print "|aaa|" + bytestr(bajty)
			sequence=bajty[0]*256 + bajty[1]
			length=bajty[4]*256 + bajty[5]
			if self.lastsequence != sequence:
				raise MbclientFail("Sequence mismatch: expected "+str(self.lastsequence)+", got "+str(sequence),FAILCODE_TCPSEQUENCE)										
			if length:				 			
				bstr=self.transportRead(length,self.charTout * 256)
				#print 'bytes : ',len(bstr)
				if bstr != '':
					if len(bstr)<length:
						raise MbclientFail("Not enough bytes received ",FAILCODE_NODATA)						
					bajtydata=bytearray(bstr)
					#print "|bbb|"+bytestr(bajtydata)
					apdu=bajtydata
					rtu = mbusbase.receivedRtu(apdu, True)
					rtu.clientParse()
					return rtu
			else:
				raise MbclientFail("TCP header length = 0 ",FAILCODE_LENGTH)						
										
		return reply



def setTimeout(self, tout):
    self.timeout = tout

class mbclientserial(mbclient):
	portdev=None
	def transportOpen(self, device, brate=9600, stopbit=1, timeout=0.9, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE):
		self.mainTout=timeout
		self.charTout=12*1/brate
		self.portdev=None
		try:
			self.portdev = serial.Serial(device,  timeout = timeout, baudrate=9600, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE)
                        if not hasattr(self.portdev, 'setTimeout'):
                           serial.Serial.setTimeout = setTimeout
		except Exception as inst:
			self.portdev = None
			raise MbclientFail("Can't open serial "+str(device)+" ["+inst.args[1]+']',FAILCODE_SERIAL)
		# flush some garbage 
		self.portdev.setTimeout(0.01)			
		self.portdev.read(16)
		# configure for good
		self.portdev.setTimeout(timeout)			
		self.portdev.baudrate=brate
		self.portdev.parity=parity  #serial.PARITY_EVEN
		self.portdev.stopbits=stopbits
		self.transportOpen=True

	def transportClose(self):
		try:
			self.portdev.close()
		except:
			pass
		return None

		
		
	def transportSend(self, rawbytes):
		if not self.transportOpen:
			return None
		try:
			bb=bytearray(1)
			for b in rawbytes:
				bb[0]=b
				self.portdev.write(bb)
			#return self.portdev.write(rawbytes)
			return
		except Exception as inst:		
			raise MbclientFail("Can't write serial ["+inst.args[1]+']',FAILCODE_SERIALWRITE)
		return None


	def transportRead(self, count,timeout):
		
		if not self.transportOpen:
			return None
		try:
			if timeout:
				if	timeout==self.TOUTMSG:  self.portdev.setTimeout(self.mainTout)
				elif  timeout==self.TOUTCHAR: self.portdev.setTimeout(self.charTout * count)
				else: self.portdev.setTimeout(timeout) 
			return self.portdev.read(count)
		except Exception as inst:		
			raise MbclientFail("Can't read serial ["+inst.args[1]+']',FAILCODE_SERIALREAD)
		return None


	def sendRequest(self, request):
		bytes=request.rtu();
		return self.transportSend(bytes)		

	def awaitReply(self):
		reply=self.getReply()
		return reply




class mbclientdevice(object):
	def __init__(self, mbaddr, mbclientiface):
		self.mbaddr = mbaddr
		self.mbclientiface = mbclientiface




if __name__ == "__main__":
	tecl = mbclientserial()
	tecl.transportOpen('/dev/ttyUSB0', brate=9600)
	#r03 = mbusbase.request01(1,0x3,20)
	r03 = mbusbase.request03(1,1,10)
	print bytestr(r03.rtu())
	tecl.transportSend(r03.rtu())
	reply=tecl.getReply()
	if reply:
		if reply.fail:
			print 'dupa' + str(reply.fail)
		else:
			print reply.vals 				 			

	#time.sleep(0.5)
	pass
