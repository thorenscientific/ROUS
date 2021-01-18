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

# Python code to talk to LT3099 trim circuit via ADALM2000
# Gets address, data and then pushes Morse code out to LT3099
#
# Code to LT3099 is 0.5usec pulse for zero, 1.5usec pulse for one
# pulses are in a 5usec window
# base level of code is 1V to 3V

import libm2k

n_bits=4

sr = 2000000 # 2Msps gives us 0.5us resolution
zero = [1,0,0,0,0,0,0,0,0,0]
one =  [1,1,1,0,0,0,0,0,0,0]
nul = [0,0,0,0,0,0,0,0,0,0]
frm = one





ctx=libm2k.m2kOpen()
if ctx is None:
	print("Connection Error: No ADALM2000 device available/connected to your PC.")
	exit(1)

dig=ctx.getDigital()

dig.setSampleRateIn(sr)
dig.setSampleRateOut(sr)

for i in range(4):
    dig.setDirection(i,libm2k.DIO_OUTPUT)
    dig.enableChannel(i,True)

buff=range(2**n_bits) # create 3 bit binary counter

buff = zero + one + nul + nul + nul + one + zero + nul + nul + nul


dig.setCyclic(True)
dig.push(buff)

data = dig.getSamples(256)

for val in data:
    print(bin(val))
