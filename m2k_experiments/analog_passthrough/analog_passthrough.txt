#
# Copyright (c) 2019 Analog Devices Inc.
#
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

# This example assumes the following connections:
# W1 -> 100-ohm resistor in series with speaker
# W2 -> open
# 2+ -> Microphone
# GND -> 1-
# GND -> 2-
#
# The application will record a few seconds of audio on scope channel 2, reverse the order of the samples,
# Apply some filtering tricks to remove large DC offsets, then play back. Playback is at 75% of record speed just due
# to available sample rates, so a future upgrade would be to do a bit of multirate processing:
# 10ksps upsampled by 3, interpolated, then downsampled by 4 should do the trick :)

import libm2k
import matplotlib.pyplot as plt
import time
import numpy as np

ctx=libm2k.m2kOpen("ip:192.168.3.231")
if ctx is None:
	print("Connection Error: No ADALM2000 device available/connected to your PC.")
	exit(1)

ctx.calibrateADC()
ctx.calibrateDAC()

ain=ctx.getAnalogIn()
aout=ctx.getAnalogOut()
trig=ain.getTrigger()
ps=ctx.getPowerSupply()

ps.enableChannel(0,True) #Consider using for microphone power,
ps.pushChannel(0,4.0) # unfortunately DC blocking cap takes forever to charge


ain.enableChannel(0,True)
ain.enableChannel(1,True)
ain.setSampleRate(10000000)    # 1Msps is REALLY fast for audio, but we're going to filter and downsample for two reasons:
ain.setOversamplingRatio(133) # First, to reduce noise. Second, to reconcile the difference in available sample rates between
ain.setRange(1,-1,1)          # input and outputs.


print("ain sample rate: " + str(ain.getSampleRate()))
print("ain range: " + str(ain.getRangeLimits(1)))

print("Starting...")
time.sleep(0.1)


bufflen = 2**8



aout.setSampleRate(0, 75000)
aout.setSampleRate(1, 75000)
aout.enableChannel(0, True)
aout.enableChannel(1, True)

print("aout sample rate: " + str(aout.getSampleRate()))

aout.setCyclic(False)

for i in range(10000): # gets 10 triggered samples then quits

    data = ain.getSamples(bufflen)
    aout.push(data)



libm2k.contextClose(ctx)
