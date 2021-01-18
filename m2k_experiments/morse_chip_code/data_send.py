# Python code to talk to LT3099 trim circuit via ADALM2000
# Gets address, data and then pushes Morse code out to LT3099
#
# Code to LT3099 is 0.5usec pulse for zero, 1.5usec pulse for one
# pulses are in a 5usec window
# base level of code is 1V to 3V

def getaddr():
    goodad = False
    while not goodad:
        addrin = input("Please enter an address location (0-31) or type end to quit:")
        if addrin == "end":
            return 32
        else:
            if addrin.isdigit():
                addr = int(addrin)
                if addr < 0 or addr > 32:
                    print("Bad Address")
                else:
                  return addr
            else:
                print("Bad Address")

def getdata(address):
    baddata = True
    while baddata:
        datain = input("Please enter the data for location %d (0 or 1):" % address)
        if datain.isdigit():
            dataval = int(datain)
            if dataval == 0 or dataval == 1:
                return dataval
            else:
                print("Bad data")
        else:
            print("Bad data")

def datapush(address,data,zerodata,onedata):
    buffer = [onedata,onedata]
    aout.push(buffer)
    buffer = [zerodata,zerodata]
    aout.push(buffer)
    if address > 15:
        B4 = 1
        buffer = [onedata,onedata]
        address = address - 16
    else:
        B4 = 0
        buffer = [zerodata,zerodata]
    aout.push(buffer)
    if address > 7:
        B3 = 1
        buffer = [onedata,onedata]
        address = address - 8
    else:
        B3 = 0
        buffer=[zerodata,zerodata]
    aout.push(buffer)
    if address > 3:
        B2 = 1
        buffer = [onedata,onedata]
        address = address - 4
    else:
        B2 = 0
        buffer=[zerodata,zerodata]
    aout.push(buffer)
    if address > 1:
        B1 = 1
        buffer = [onedata,onedata]
        address = address -2
    else:
        B1 = 0
        buffer=[zerodata,zerodata]
    aout.push(buffer)
    if address == 1:
        buffer = [onedata,onedata]
    else:
        buffer=[zerodata,zerodata]
    aout.push(buffer)
    if data == 1:
        buffer = [onedata,onedata]
    else:
        buffer=[zerodata,zerodata]
    aout.push(buffer)
    parity = (B4+B3+B2+B1+address+data)%2
    if parity == 1:
        buffer = [onedata,onedata]
    else:
        buffer=[zerodata,zerodata]
    aout.push(buffer)
    buffer = [onedata,onedata]
    aout.push(buffer)
    print ("Type    | Value")
    print ("Frame   |   1")
    print ("MSB(B5) |   0")
    print ("B4      |   %d" % B4)
    print ("B3      |   %d" % B3)
    print ("B2      |   %d" % B2)
    print ("B1      |   %d" % B1)
    print ("LSB(B0) |   %d" % address)
    print ("Data    |   %d" % data)
    print ("Parity  |   %d" % parity)
    print ("Frame   |   1")


import libm2k
import numpy as np
import sys
ctx=libm2k.m2kOpen()
if ctx is None:
	sys.exit("Connection Error: No ADALM2000 device available/connected to your PC.")
zerodata = np.ones([375])
onedata = np.ones([375])
zerodata[6:43]=3
onedata[6:118]=3

ctx.calibrateADC()
ctx.calibrateDAC()

ain=ctx.getAnalogIn()
aout=ctx.getAnalogOut()
trig=ain.getTrigger()

aout.setSampleRate(0, 3750000) #Use 1 for debug w/DMM, otherwise 3750000
aout.setSampleRate(1, 3750000) #Use 1 for debug w/DMM, otherwise 3750000
aout.enableChannel(0, True)
aout.enableChannel(1, True)
aout.setCyclic(False)

address = 33

while address > 32:
    address = getaddr()
    if address < 32:
        data = getdata(address)
        print ("Entering a %d into location %d" % (data, address))
        datapush(address,data,zerodata,onedata)
        address = 33

print("Game over man!!!")
libm2k.contextClose(ctx)