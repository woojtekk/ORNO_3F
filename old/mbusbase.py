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

from old.crc16 import *
import ctypes


FAILCODE_CRC    = 1
FAILCODE_REPLY  = 3


class MbusbaseFail(Exception):
    def __init__(self, message, code, fail=0, reply=None):
        super(MbusbaseFail, self).__init__(message)
        self.code    = code
        self.fail    = reply
        self.reply   = reply  

def bytestr(bytes):
    ot=''
    for by in bytes:
        ot=ot+('%02X ' % by)
    return ot


class errcode(object): 
	NOERROR                           =0x00
	ILLEGAL_FUNCTION                  =0x01
	ILLEGAL_DATA_ADDRESS              =0x02
	ILLEGAL_DATA_VALUE                =0x03
	SLAVE_DEVICE_FAILURE              =0x04
	ACKNOWLEDGE                       =0x05
	SLAVE_DEVICE_BUSY                 =0x06
	MEMORY_PARITY_ERROR               =0x08
	GATEWAY_PATH_UNAVAILABLE          =0x0A
	GATEWAY_TARGET_FAILED_TO_RESPOND  =0x0B
	names={
		NOERROR                           :'no error',
		ILLEGAL_FUNCTION                  :'illegal function',
		ILLEGAL_DATA_ADDRESS              :'bad data address',
		ILLEGAL_DATA_VALUE                :'bad data value',
		SLAVE_DEVICE_FAILURE              :'slave failure',
		ACKNOWLEDGE                       :'acknowledge',
		SLAVE_DEVICE_BUSY                 :'slave device busy',
		MEMORY_PARITY_ERROR               :'memory parity',
		GATEWAY_PATH_UNAVAILABLE          :'gateway path unavailable',
		GATEWAY_TARGET_FAILED_TO_RESPOND  :'gateway target failed to respond',
		}
	pass



def makeFrame8(addr, code, data):
    lent=1+1+len(data);    
    bytes=bytearray(lent);
    bytes[0] =  addr;
    bytes[1] =  code;
    idx=0;
    for dat in data:
        bytes[2] = dat & 0xFF;        
        idx+=1
    return bytes


def makeFrame16(addr, code, data):
    lent=1+1+len(data)*2;    
    bytes=bytearray(lent);
    bytes[0] =  addr;
    bytes[1] =  code;
    idx=0;
    for dat in data:
        bytes[2+idx] = dat >> 8;
        bytes[3+idx] = dat & 0xFF;
        idx+=2
    return bytes


def makeFrameAppendStart(addr, code):        
    bytes=bytearray();
    if addr:
    	bytes.append(addr)
	bytes.append(code)
    return bytes 


def makeFrameAppend8(data, value):
	data.append(value)
	return data        



def makeFrameAppend16(data, value):
	if value<0: value=ctypes.c_ushort(value).value 
	data.append(value >> 8)
	data.append(value & 0xFF)
	return data        


def makeRtuFrame(frmabytes):
    lent=len(frmabytes)
    frmabytes.append(0)
    frmabytes.append(0)
    crc = INITIAL_MODBUS
    for ix in xrange(0,lent):
        crc = calcByte( frmabytes[ix], crc)
    frmabytes[lent] = crc & 0xFF
    frmabytes[lent+1] = crc >> 8 
    return frmabytes


def makeTcpFrame(frmabytes, sequence):
	lent=len(frmabytes)
	frmabytes.insert(0,lent)
	frmabytes.insert(0,0)
	frmabytes.insert(0,0)
	frmabytes.insert(0,0)
	frmabytes.insert(0,sequence & 0xFF)
	frmabytes.insert(0,sequence >> 8)
	return frmabytes


def get16(arrayin):
	try:
		return (arrayin[2:], (arrayin[0]<<8) | arrayin[1])
	except:
		return (arrayin, None)

def get8(arrayin):
	try:
		return (arrayin[1:], arrayin[0]) 
	except:
		return (arrayin, None)


class framebase(object):	
	def __init__(self,adres,code):
		self.bytes = makeFrameAppendStart(adres,code)
		self.tcpseq=0
	 	pass;
	def rtu(self):
		return makeRtuFrame(self.bytes)
	def tcp(self, sequence):
		self.tcpseq=sequence
		return makeTcpFrame(self.bytes, sequence)


class response(framebase):
	reqCode = 0x01


#-----------------------------------------------------
# 80  - error response

class responseError(response):
	def __init__(self,adres,reqCodeRep,errCodek):
		self.reqCode = reqCodeRep | 0x80
		super(responseError,self).__init__(adres,self.reqCode)
		self.bytes = makeFrameAppend8(self.bytes, errCodek)


#-----------------------------------------------------
# 01  - read coils

class request01(framebase):
	reqCode = 0x01
	def __init__(self,adres,val16_1,val16_2):
		super(request01,self).__init__(adres,self.reqCode)
		self.bytes = makeFrameAppend16(self.bytes, val16_1)
		self.bytes = makeFrameAppend16(self.bytes, val16_2)
		#print bytestr(self.bytes)

class response01(response):
	reqCode = 0x01
	def __init__(self,adres,coilsarr):
		super(response01,self).__init__(adres,self.reqCode)
		coilcnt  = len(coilsarr) 	
		bytescnt = 1+((coilcnt -1 ) >> 3) 
		self.bytes = makeFrameAppend8(self.bytes, bytescnt)
		byteidx=0
		coilbyte=0
		for coil in coilsarr:
			if coil:
				coilbyte |= 1 << byteidx				
			byteidx+=1
			if byteidx==8:
				self.bytes = makeFrameAppend8(self.bytes, coilbyte)
				byteidx=0  
				coilbyte = 0
		if byteidx:
			self.bytes = makeFrameAppend8(self.bytes, coilbyte)


#-----------------------------------------------------
# 02  - read discrete inputs

class request02(request01):
	reqCode = 0x02


class response02(response01):
	reqCode = 0x02


#-----------------------------------------------------
# 03  - read holding registers

class request03(request01):
	reqCode = 0x03

class response03(response):
	reqCode = 0x03
	def __init__(self,adres,regarr):
		super(response03,self).__init__(adres,self.reqCode)
		regcnt = len(regarr) 	
		self.bytes = makeFrameAppend8(self.bytes, 2*regcnt)
		for reg in regarr:
			self.bytes = makeFrameAppend16(self.bytes, reg)



#-----------------------------------------------------
# 04  - read input register

class request04(request01):
	reqCode = 0x04
	
class response04(response03):
	reqCode = 0x04
	
	

#-----------------------------------------------------
# 05  - write single coil

class request05(request01):
	reqCode = 0x05
	def __init__(self,adres,addr,state):
		super(request01,self).__init__(adres,self.reqCode)
		statenumber=0x0000
		if state:
			statenumber=0xFF00 # as specified in the standard
		self.bytes = makeFrameAppend16(self.bytes, addr)
		self.bytes = makeFrameAppend16(self.bytes, statenumber)
	 	pass

class response05(response):
	reqCode = 0x05
	def __init__(self,adres,addr,state):
		super(response05,self).__init__(adres,self.reqCode)
		statenumber=0x0000
		if state:
			statenumber=0xFF00 # as specified in the standard
		self.bytes = makeFrameAppend16(self.bytes, addr)
		self.bytes = makeFrameAppend16(self.bytes, statenumber)




#-----------------------------------------------------
# 06  - write single register

class request06(request01):
	reqCode = 0x06

class response06(response):
	reqCode = 0x06
	def __init__(self,adres,addr,value):
		super(response06,self).__init__(adres,self.reqCode)
		self.bytes = makeFrameAppend16(self.bytes, addr)
		self.bytes = makeFrameAppend16(self.bytes, value)




#-----------------------------------------------------
# 15  - write multiple coils

class request15(framebase):
	reqCode = 0x0F
	def __init__(self,adres,startaddr,coilsarr):
		super(request15,self).__init__(adres,self.reqCode)
		self.bytes = makeFrameAppend16(self.bytes, startaddr)	
		coilcnt = len(coilsarr) 	
		self.bytes = makeFrameAppend16(self.bytes, coilcnt)
		bytescnt = 1+((coilcnt -1 ) >> 3) 
		self.bytes = makeFrameAppend8(self.bytes, bytescnt)
		byteidx=0
		coilbyte=0
		for coil in coilsarr:
			if coil:
				coilbyte |= 1 << byteidx				
			byteidx+=1
			if byteidx==8:
				self.bytes = makeFrameAppend8(self.bytes, coilbyte)
				byteidx=0  
				coilbyte = 0
		if byteidx:
			self.bytes = makeFrameAppend8(self.bytes, coilbyte)
	 	pass


class response15(response):
	reqCode = 0x0F
	def __init__(self,adres,addr,quantity):
		super(response15,self).__init__(adres,self.reqCode)
		self.bytes = makeFrameAppend16(self.bytes, addr)
		self.bytes = makeFrameAppend16(self.bytes, quantity)



#-----------------------------------------------------
# 16  - write multiple registers

class request16(framebase):
	reqCode = 0x10
	def __init__(self,adres,startaddr,regarr):
		super(request16,self).__init__(adres,self.reqCode)
		self.bytes = makeFrameAppend16(self.bytes, startaddr)	
		regcnt = len(regarr) 	
		self.bytes = makeFrameAppend16(self.bytes, regcnt)		
		self.bytes = makeFrameAppend8(self.bytes, 2*regcnt)
		for reg in regarr:
			self.bytes = makeFrameAppend16(self.bytes, reg)

class response16(response15):
	reqCode = 0x10



	
class received(object):
	FAIL_OK    = 0
	FAIL_CRC   = 1	
	FAIL_BAD   = 2	
	FAIL_REPLY = 3	
	fcode   = 0
	address = 0
	fail    = 0
	failCode= 0
	data    = None     
	def __init__(self):
		pass
	
#-----------------------------------------------------
# Parse RTU

class receivedRtu(received):
	def __init__(self,rxbytes, nocrc=False):
		super(receivedRtu,self).__init__()
		#print "RX:::" + bytestr(rxbytes)
		rxcnt = len(rxbytes)
		limit=4
		if nocrc: limit=3  
		if rxcnt < limit:
			self.fail = self.FAIL_BAD
			self.failCode = 1000
			self.failText = "receive RTU"
		else:			
			if not nocrc:
				crc = INITIAL_MODBUS
				for bajt in rxbytes:
					crc = calcByte( bajt, crc)
			else:
				crc=0
			if crc:
				self.fail = self.FAIL_CRC
				self.failCode = 1000
				self.failText = "CRC"
				raise MbusbaseFail('Bad CRC',FAILCODE_CRC, reply=self)
			else:
				self.address = rxbytes[0]
				self.fcode   = rxbytes[1] & 0x7F
				if rxbytes[1]>127:
					self.fail = self.FAIL_REPLY
					self.data = bytearray(rxbytes)
					errortext = 'Host replied fail: ('+str(self.FAIL_REPLY)+') '+errcode.names[self.FAIL_REPLY]
					raise MbusbaseFail(errortext,FAILCODE_REPLY, self.FAIL_REPLY, reply=self)
				else:
					if not nocrc: 
						self.data = bytearray(rxbytes[2:-2])
					else: 	 
						self.data = bytearray(rxbytes[2:])


	def clientParse(self):
		self.vals=None
		if self.fail == self.FAIL_REPLY:
			self.vals=[self.data[1] & 0x7F, self.data[2]]
			self.failCode=self.data[2]
			self.failText=errcode.names[self.failCode]   
		
		elif self.fcode==3 or self.fcode==4:
			self.vals=[]
			for byi in xrange(0,self.data[0] / 2):
				val16=self.data[1+byi*2]*256 + self.data[2+byi*2]
				self.vals.append(val16)
	
		elif self.fcode==1 or self.fcode==2:
			self.vals=[]
			for byi in xrange(0,self.data[0]):
				for biti in xrange(0,8):
					bit = (self.data[1+byi] >> biti) & 1
					self.vals.append(bit)

		elif self.fcode==5 or self.fcode==6 or self.fcode==15 or self.fcode==16:
			self.vals=[]
			#print bytestr(self.data)
			val16=self.data[0]*256 + self.data[1]
			self.vals.append(val16)
			val16=self.data[2]*256 + self.data[3]
			self.vals.append(val16)
			


def parseRtu(frrtu):
    #IF read 16 bit regs
    valstxt=''
    if frrtu[1]==0x03 or frrtu[1]==0x04:
       vals=[]
       valstxt=''
       for byi in xrange(0,frrtu[2] / 2):
           val16=frrtu[3+byi*2]*256 + frrtu[4+byi*2]
           vals.append(val16)
           valstxt+='%5u ' % val16


    if frrtu[1]==0x01 or frrtu[1]==0x02:
       vals=[]
       for byi in xrange(0,frrtu[2]):
           for biti in xrange(0,8):
               bit = (frrtu[3+byi] >> biti) & 1;
               valstxt+='%u ' % bit






#====================================================================
# 
# TESTS
# 
#====================================================================

if __name__ == "__main__":
	req = request05(0x12,0xA,1).rtu()
	print bytestr(req)	
	req = request15(0xCC,0x13,[1,0,1,1,0,0,1,1,1]).rtu()
	print bytestr(req)	
	req = request16(0xCC,0x01,[0x000A,0x0102]).rtu()
	print bytestr(req)	
	print "response"
	print bytestr(response04(0x11,[0x000A,0x0102]).rtu())	
	print bytestr(response06(0x11,0xC00A,0x4008).rtu())	
	print bytestr(response15(0x11,0xC00A,0x4008).rtu())	
	print bytestr(response16(0x11,0xC00A,0x4008).rtu())	
	
	 
	rxrtu = receivedRtu( req ) 
	
	print bytestr(rxrtu.data)
	
	pass

		
		
		
			
