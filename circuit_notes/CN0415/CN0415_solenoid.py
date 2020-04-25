# -*- coding: utf-8 -*-
"""
    Description:
        Shave and a haircut on CN0415
    
    Created by: 
    E-mail: 

<<License goes here>>

"""
###############################################################################
# Libraries
###############################################################################
import serial
import time

myport='COM17'

def write_slow(s, st):
    for c in st:
        s.write(c)
        time.sleep(0.001)
        s.read(1) # eat echoed character
        time.sleep(0.001)
    s.read(1) # eat ">" at the end...

def knock(s):
    write_slow(s, "d 9000\n")
    time.sleep(0.1)
    write_slow(s, "d 10\n")

def tone(s, t, f):
    write_slow(s, "f " + f + "\n")
    time.sleep(t)
    write_slow(s, "f 10000\n") #Go ultrasonic (to most humans) but keep actuated

# Constants and stuff
delay = 0.1 # unit delay
delaytab = [3*delay, 1*delay, 1*delay, 3*delay, 6*delay, 3*delay, 0*delay]
notes=["523", "392", "392", "440", "392", "494", "523"]

ser = serial.Serial(port=myport, timeout=1.0)  # open serial port
ser.baudrate = 9600
print(ser.name)         # check which port was really used
time.sleep(1)
str = ser.read(100)
print("string read out:")
print(str)

delay = 0.1 # unit delay
delaytab = [3*delay, 1*delay, 1*delay, 3*delay, 6*delay, 3*delay, 1*delay]
notes=["523", "392", "392", "440", "392", "494", "523"]

# KnockKnock version
for i in range (0, 7):
    knock(ser)
    time.sleep(delaytab[i])


time.sleep (1)
write_slow(ser, "d 9000\n") #Pull in solenoid
time.sleep(0.25)
write_slow(ser, "d 5000\n") #Maximum ripple current
time.sleep(0.5)

#Musical version
for i in range (0, 7):
    tone(ser, 0.1, notes[i])
    time.sleep(delaytab[i])

write_slow(ser, "d 100\n") # De-actuate solenoid

str = ser.read(100)
print("string read out:")
print(str)

ser.close()


