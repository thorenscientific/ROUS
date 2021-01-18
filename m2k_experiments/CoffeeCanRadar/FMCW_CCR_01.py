#
# Copyright (c) 2019 Analog Devices Inc.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# FMCW RADAR example!!
# Start by constructing the RF portion of Greg Charvat's most excellent course on small radar systems:
# https://ocw.mit.edu/resources/res-ll-003-build-a-small-radar-system-capable-of-sensing-range-doppler-and-synthetic-aperture-radar-imaging-january-iap-2011/index.htm
# Drive VCO tune pin from W1 output through a 1k:1k divider referenced to +5V
# (This translates +/-5V output to 0-5V at the tune pin, maximizing resolution)
# Video amplifier is an LT1677 in a noninverting gain of 50,
# mixer IF output coupled through 1uF/10k highpass. UNLIKE the coffee can radar,
# we have megasamples per second, don't bother with the 4th order filter, we can
# do that in the digital :)
# Connect W2 to 2+ as a cheesy trigger. (should clean that up later, can we sync
# trigger to buffer push??)

import libm2k
import pickle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import time
import numpy as np

def pickle_me(fname, obj):
    f = open(fname, 'wb')
    pickle.dump(f, obj)
    f.close()

try:
    ctx
except:
    ctx=libm2k.m2kOpen()
    if ctx is None:
    	print("Connection Error: No ADALM2000 device available/connected to your PC.")
    	exit(1)

    ctx.calibrateADC()
    ctx.calibrateDAC()

    ain=ctx.getAnalogIn()
    aout=ctx.getAnalogOut()
    trig=ain.getTrigger()
    ps = ctx.getPowerSupply()

ain.enableChannel(0,True)
ain.enableChannel(1,True)
ain.setSampleRate(1000000) # 1Msps
ain.setOversamplingRatio(10) # divide by 10 = 100ksps
ain.setRange(0,-10,10)

ps.enableChannel(0,True)
ps.enableChannel(1,True)
ps.pushChannel(0,5.0)
ps.pushChannel(1,-5.0)

print("Waiting for PS to stabilize...")
time.sleep(2.0)
print("Done!")

### uncomment the following block to enable triggering
trig.setAnalogSource(1) # Channel 1 as source
trig.setAnalogCondition(1,libm2k.RISING_EDGE_ANALOG)
trig.setAnalogLevel(1,0.5)  # Set trigger level at 0.5
trig.setAnalogDelay(0) # Trigger is centered
trig.setAnalogMode(1, libm2k.ANALOG)

aout.setSampleRate(0, 750000)
aout.setSampleRate(1, 750000)
aout.enableChannel(0, True)
aout.enableChannel(1, True)


vt_min = -3.0
vt_max = 3.0
ramplen = 37500
settle = 10000
x=np.linspace(-np.pi,np.pi,ramplen)
buffer1=np.concatenate((np.ones(settle)*vt_min, np.linspace(vt_min,vt_max,ramplen)))
buffer2=np.concatenate((np.zeros(settle+100), np.ones(1000), np.zeros(ramplen-1100)))

buffer = [buffer1, buffer2]

aout.setCyclic(True)
aout.push(buffer)
range_data = []
plt.figure(1)

numsweeps = 256
datalen = 8192
fftlen = 4096
padlen = 4096

for i in range(numsweeps): # gets 10 triggered samples then quits
    print("waiting for trigger...")
    data = ain.getSamples(datalen)
    print("Triggered!", i)
    plt.plot(data[0])
    plt.plot(data[1])
    plt.show()
    time.sleep(0.25)
    range_data.append(data[0])

scene = []
plt.figure(2)
for i in range(numsweeps):
    scene.append(range_data[i][0:fftlen])
    scene[i] -= np.average(scene[i]) # remove DC
    scene[i] *= np.hanning(fftlen) # Apply window
    scene[i] = np.abs(np.fft.fft(np.concatenate((scene[i], np.zeros(padlen)))))[0:int(fftlen/2)]
    scene[i] = 20*np.log10(scene[i])
    plt.plot(scene[i])

plt.figure (3)

fig, ax = plt.subplots()
im = ax.imshow(scene, interpolation='bilinear', cmap=cm.plasma, origin='lower', extent=[0, fftlen/2, 0, numsweeps])#,
#               vmax=abs(scene).max(), vmin=-abs(scene).max())

# RdYlGn

plt.show()

libm2k.contextClose(ctx)
