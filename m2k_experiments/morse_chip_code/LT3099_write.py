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



n_bits=4

sr = 2000000 # 2Msps gives us 0.5us resolution
zero = [3,2,2,2,2,2,2,2,2,2]
one =  [3,3,3,2,2,2,2,2,2,2]
nul = [2,2,2,2,2,2,2,2,2,2]
off = [0,0,0,0,0,0,0,0,0,0]
frm = one


def lt3099_write(ctxin=None, regs=[]):
    import libm2k
    if ctxin==None:
        ctx=libm2k.m2kOpen()
    else:
        ctx=ctxin

    if ctx is None:
    	print("Connection Error: No ADALM2000 device available/connected to your PC.")
    	exit(1)

    dig=ctx.getDigital()

    dig.setSampleRateIn(sr)
    dig.setSampleRateOut(sr)

    for i in range(4):
        dig.setDirection(i,libm2k.DIO_OUTPUT)
        dig.enableChannel(i,True)

    buff = nul + nul + nul # Set enable line high

    for reg in regs:
        buff += (frm) # Frame bit
        addr = reg[0] # Extract address
        data = reg[1] # Extract data bit
        bitcnt = 0 # Counter for parity
        for bit in range(6): # Parse through address bits
            if (addr & 0b100000 >> bit) != 0:
                buff += (one)
                bitcnt += 1
            else:
                buff += (zero)
        if data == 1: # Set data bit accordingly
            buff += (one)
            bitcnt += 1
        else:
            buff += (zero)
        if bitcnt % 2 == 0: # detect even parity
            buff += (one)
        buff += (frm) # Final frame bit
        buff += (nul) # Null for good luck

    buff += (nul) # Couple of extra nulls for good luck
    buff += (nul)
    buff += (off) # Disable D1 (programming bit.)

# UN-comment to print out buffer.
#    print("Buffer:")
#    print(buff)

    dig.setCyclic(False)
    dig.push(buff)

    if ctxin==None: # Clean up context if not passed from main program
        libm2k.contextClose(ctx)


# Test program. If you run this module by itself, it will run this code.
# If imported from a higher level program, you get the one and only
# lt3099_write() function. Leave ctxin undefined to open / close the M2K with
# each call, this should be fine for now.

#NOTE that there's still a bug in closing down the context - for some reason
# the M2K is not "released", you have to cycle USB after each call.

if __name__ == '__main__':
    x = [[0,0],[1,1],[2,0],[3,1]]
    lt3099_write(regs=x)
    print("Done!")
