#
# Copyright (c) 2019 Analog Devices Inc.
#
# This file is part of libm2k
# (see http://www.github.com/analogdevicesinc/libm2k).
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

# 40 kHz Phased Array on the Cheap!

import libm2k
import matplotlib.pyplot as plt
import time
import numpy as np

ctx=libm2k.m2kOpen()
if ctx is None:
	print("Connection Error: No ADALM2000 device available/connected to your PC.")
	exit(1)


ain=ctx.getAnalogIn()
aout=ctx.getAnalogOut()
trig=ain.getTrigger()

# Prevent bad initial config for ADC and DAC
ain.reset()
aout.reset()

ctx.calibrateADC()
ctx.calibrateDAC()

ps=ctx.getPowerSupply()
ps.reset()
ps.enableChannel(0,True)
ps.enableChannel(1,True)
ps.pushChannel(0,4.5)
ps.pushChannel(1,-4.5)


ain.enableChannel(0,True)
ain.enableChannel(1,True)
ain.setSampleRate(100000)
ain.setRange(0,-2,2)

### uncomment the following block to enable triggering
#trig.setAnalogSource(0) # Channel 0 as source
#trig.setAnalogCondition(0,libm2k.RISING_EDGE_ANALOG)
#trig.setAnalogLevel(0,0.5)  # Set trigger level at 0.5
#trig.setAnalogDelay(0) # Trigger is centered
#trig.setAnalogMode(1, libm2k.ANALOG)

aout.setSampleRate(0, 750000)
aout.setSampleRate(1, 750000)
aout.enableChannel(0, True)
aout.enableChannel(1, True)


fs_dac, fs_adc = 750_000.0, 1_000_000.0
N_adc = 4096
N_dac = 3 * N_adc // 4      # 3072, always a multiple of 4
M     = 163                 # cycles in the buffer (prime -> clean spectrum)
f     = M * fs_adc / N_adc  # 39794.921875 Hz

n   = np.arange(N_dac)
bufp = np.sin(2*np.pi*M*n/N_dac)   # exactly M cycles, seamless wrap
bufn = bufp * -1.0

x=np.linspace(-np.pi,np.pi,1024)
buffer1=np.linspace(-2.0,2.00,1024)
buffer2=np.sin(x)

buffer = [bufp, bufn]

aout.setCyclic(True)
aout.push(buffer)

for i in range(10): # gets 10 triggered samples then quits
    print("Run: ", i)
    data = ain.getSamples(N_adc)
    plt.plot(data[0])
#    plt.plot(data[1])
    plt.show()
    time.sleep(0.1)

libm2k.contextClose(ctx)
