#!/usr/bin/env python
# encoding: utf-8
#hahahaha
#hahahaha
#hahahaha
#hahahaha
#hahahaha
#---------------------------------#---------------------------------#---------------------------------
#---------------------------------

import serial
import mbusbase
import mbusclient


energyclient = None


def createClient(portDevice, adres):
	tecl = mbusclient.mbclientserial()
	tecl.adres = adres
	tecl.transportOpen(portDevice, brate=9600, parity=serial.PARITY_EVEN)
	return tecl

	

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
	print( "Energy MODBUS: " + portDevice)
	mbcli = createClient(portDevice, adres)
	if mbcli!=None:
		global energyclient
		energyclient = mbcli
		return mbcli


if __name__ == "__main__":
   mbcli = startClient("/dev/ttyUSB0", 1)
   print()
   print("ID ORNO ... ", readRegs(mbcli, 0x0110, 1))
   print("Grind Frequency ... ", readRegs(mbcli, 14, 1))
   print("Voltage ... ", readRegs(mbcli, 0x0131, 1))
   print("Current ... ", readRegs(mbcli, 0x0139, 1))
   print("Active Power ... ", readRegs(mbcli, 0x0140, 1))
   print("Reactive Power ... ",  readRegs(mbcli, 0x0148, 1))
   print("Apparent Power ... ",  readRegs(mbcli, 0x0150, 1))
   print("Power Factor ... ",  readRegs(mbcli, 0x0158, 1))
   print("Active Energy ... ",  readRegs(mbcli, 0xA000, 1))
   print("Reactive Energy ... ",  readRegs(mbcli, 0xA01E, 1))
