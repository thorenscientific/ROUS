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

# This example will generate a binary counter on the first N_BITS of the
# digital interface and read them back - no additional connection required

import libm2k

# Initial test data. We'll button this up into a function shortly.
my_data = [1, 0, 0, 1, 0, 0, 0, 0]

# Available sample rates: 1000 10000 100000 1000000 10000000 100000000
SampleRateOut = 10000

clock_setup = 1 # Low cycles to place before data
clock_high = 1 # High cycles during valid data
clock_hold = 1 # Low cycles to place after data
    

# Initialize buffer
buf = []

# Build pattern to send to the pattern generator
for data_bit in my_data:
    buf.extend([0 | data_bit << 1]*clock_setup)
    buf.extend([1 | data_bit << 1]*clock_high)
    buf.extend([0 | data_bit << 1]*clock_hold)

# UN-comment for debug purposes
'''
for val in buf:
    print(bin(val))
'''

# Open m2k
ctx=libm2k.m2kOpen()
if ctx is None:
	print("Connection Error: No ADALM2000 device available/connected to your PC.")
	exit(1)

dig=ctx.getDigital()
dig.reset()

dig.setSampleRateOut(SampleRateOut)

for i in [0, 1, 2, 3]:
    dig.setDirection(i,libm2k.DIO_OUTPUT)
    dig.enableChannel(i,True)

dig.push(buf)

print("Done!")
# Clean up context
libm2k.contextClose(ctx, True)
