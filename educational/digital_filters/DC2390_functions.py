# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Copyright (c) 2017-2019 Analog Devices, Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Modified versions of the software must be conspicuously marked as such.
# - This software is licensed solely and exclusively for use with
#   processors/products manufactured by or for Analog Devices, Inc.
# - This software may not be combined or merged with other code in any manner
#   that would cause the software to become subject to terms and conditions
#    which differ from those listed here.
# - Neither the name of Analog Devices, Inc. nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
# - The use of this software may or may not infringe the patent rights of one
#   or more patent holders. This license does not release you from the
#   requirement that you obtain separate licenses from these patent holders
#   to use this software.
# 
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES, INC. AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# NON-INFRINGEMENT, TITLE, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ANALOG DEVICES, INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# DAMAGES ARISING OUT OF CLAIMS OF INTELLECTUAL PROPERTY RIGHTS INFRINGEMENT;
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# 2019-01-10-7CBSD SLA
# -----------------------------------------------------------------------

'''
DC2390 functions and defines. 
These are highly specific to the DC2390 and associated FPGA design.


Tested with Python 2.7, Anaconda distribution available from Continuum Analytics,
http://www.continuum.io/
'''

from time import sleep
import time
import ctypes

# Map out your registers here. These correspond directly to base addresses
# in the LTQSys_blob. Read and write values to these addresses, and signals in
# your design wiggle accordingly.
#NEW REGISTER MAP!! (after remapping to generic port names)
#control register offsets

EXPANDER_CTRL_BASE = 0x00
REV_ID_BASE = 0x10
CONTROL_BASE = 0x20
DATA_READY_BASE = 0x30
LED_BASE = 0x40
NUM_SAMPLES_BASE = 0x50
PID_KP_BASE = 0x60
PID_KI_BASE = 0x70
PID_KD_BASE = 0x80
PULSE_LOW_BASE = 0x90
PULSE_HIGH_BASE = 0xA0
PULSE_VAL_BASE = 0xB0
SYSTEM_CLOCK_BASE = 0xC0
DATAPATH_CONTROL_BASE = 0xD0
LUT_ADDR_DATA_BASE = 0xE0
TUNING_WORD_BASE = 0xF0
BUFFER_ADDRESS_BASE = 0x00000100
SPI_PORT_BASE = 0x00000800
SPI_RXDATA = 0x00
SPI_TXDATA = 0x04
SPI_STATUS = 0x08
SPI_CONTROL = 0x0C
SPI_SS = 0x14

CW_EN_TRIG = 0x00000002
CW_START = 0x00000001

# A text list for above register map
register_list = [
'REV_ID_BASE          ',
'CONTROL_BASE         ',
'DATA_READY_BASE      ',
'LED_BASE             ',
'NUM_SAMPLES_BASE     ',
'PID_KP_BASE          ',
'PID_KI_BASE          ',
'PID_KD_BASE          ',
'PULSE_LOW_BASE       ',
'PULSE_HIGH_BASE      ',
'PULSE_VAL_BASE       ',
'SYSTEM_CLOCK_BASE    ',
'DATAPATH_CONTROL_BASE',
'LUT_ADDR_DATA_BASE   ',
'TUNING_WORD_BASE     ',
'BUFFER_ADDRESS_BASE  ',
'SPI_PORT_BASE        ',
'SPI_RXDATA           ',
'SPI_TXDATA           ',
'SPI_STATUS           ',
'SPI_CONTROL          ',
'SPI_SS               ']



# LTC2500 Control Word Bitfields. These are defined such that they can be ORed
# directly into the LED_BASE register, no shifting required.

# LTC2500 DGC / DGE Bitmap
LTC2500_DGC           = 0b1000000000000000
LTC2500_DGE           = 0b0100000000000000

# LTC2500 DSF Bitmap
LTC2500_DF_4            = 0b00100000000000
LTC2500_DF_8            = 0b00110000000000
LTC2500_DF_16           = 0b01000000000000
LTC2500_DF_32           = 0b01010000000000
LTC2500_DF_64           = 0b01100000000000
LTC2500_DF_128          = 0b01110000000000
LTC2500_DF_256          = 0b10000000000000
LTC2500_DF_512          = 0b10010000000000
LTC2500_DF_1024         = 0b10100000000000
LTC2500_DF_2048         = 0b10110000000000
LTC2500_DF_4096         = 0b11000000000000
LTC2500_DF_8192         = 0b11010000000000
LTC2500_DF_16384        = 0b11100000000000

# A handy class associating DF and bitfields, with text that can
# be used to build filename of filter coefficient file
class Downsample_Factor_information:
    def __init__(self, df, df_ctrl_bits, df_txt):
        self.DF = df
        self.DF_ctrl_bits = df_ctrl_bits
        self.DF_txt = df_txt
    
DF4   = Downsample_Factor_information(4,     LTC2500_DF_4,     "4")
DF8   = Downsample_Factor_information(8,     LTC2500_DF_8,     "8")
DF16  = Downsample_Factor_information(16,    LTC2500_DF_16,    "16")
DF32  = Downsample_Factor_information(32,    LTC2500_DF_32,    "32")
DF64  = Downsample_Factor_information(64,    LTC2500_DF_64,    "64")
DF128 = Downsample_Factor_information(128,   LTC2500_DF_128,   "128")
DF256 = Downsample_Factor_information(256,   LTC2500_DF_256,   "256")
DF512 = Downsample_Factor_information(512,   LTC2500_DF_512,   "512")
DF1k  = Downsample_Factor_information(1024,  LTC2500_DF_1024,  "1024")
DF2k  = Downsample_Factor_information(2048,  LTC2500_DF_2048,  "2048")
DF4k  = Downsample_Factor_information(4096,  LTC2500_DF_4096,  "4096")
DF8k  = Downsample_Factor_information(8192,  LTC2500_DF_8192,  "8192")
DF16k = Downsample_Factor_information(16384, LTC2500_DF_16384, "16384")

# LTC2500 Filter Type Bitmap
LTC2500_SINC_FILT       = 0b00000001000000
LTC2500_SINC2_FILT      = 0b00000010000000
LTC2500_SINC3_FILT      = 0b00000011000000
LTC2500_SINC4_FILT      = 0b00000100000000
LTC2500_SSINC_FILT      = 0b00000101000000
LTC2500_SSCIN_FLAT_FILT = 0b00000110000000
LTC2500_VAR_DECIM_FILT  = 0b00000111000000

# A handy class associating filter type and bitfields, with text that can
# be used to build filename of filter coefficient file
class Filt_Type_information:
    def __init__(self, ft_ctrl_bits, ft_txt):
        self.FT_ctrl_bits = ft_ctrl_bits
        self.FT_txt = ft_txt

FTSINC1 = Filt_Type_information(LTC2500_SINC_FILT, "sinc1")
FTSINC2 = Filt_Type_information(LTC2500_SINC2_FILT, "sinc2")
FTSINC3 = Filt_Type_information(LTC2500_SINC3_FILT, "sinc3")
FTSINC4 = Filt_Type_information(LTC2500_SINC4_FILT, "sinc4")
FTSSINC = Filt_Type_information(LTC2500_SSINC_FILT, "ssinc")
FT_FLAT = Filt_Type_information(LTC2500_SSCIN_FLAT_FILT, "ssinc_flat")
        

# PID controller setpoint source
DC2390_PID_PULSE_GEN    = 0x00000000
DC2390_PID_VALUE_TRIGD  = 0x00010000
DC2390_PID_VALUE_TRIGD  = 0x00020000
DC2390_PID_ZERO         = 0x00030000

# LUT Run configuration
DC2390_LUT_RUN_CONT = 0x00000000
DC2390_LUT_RUN_ONCE = 0x00008000

# LUT Address select
DC2390_LUT_ADDR_COUNT = 0x00000000
DC2390_LUT_DIST_CORR  = 0x00001000
DC2390_LUT_CONS_H4000 = 0x00002000
DC2390_LUT_CONS_HC000 = 0x00003000

# DAC A source
DC2390_DAC_A_NCO_SIN         = 0x00000000
DC2390_DAC_A_PID             = 0x00000100
DC2390_DAC_A_PULSE_VAL_TRIGD = 0x00000200
DC2390_DAC_A_PULSE_VAL       = 0x00000300

# DAC B source
DC2390_DAC_B_NCO_COS    = 0x00000000
DC2390_DAC_B_LUT        = 0x00000010
DC2390_DAC_B_CONS_HC000 = 0x00000020
DC2390_DAC_B_CONS_H4000 = 0x00000030

# FIFO data select
DC2390_FIFO_ADCA_NYQ       = 0x00000000
DC2390_FIFO_ADCB_NYQ       = 0x00000001
DC2390_FIFO_ADCA_FIL       = 0x00000002
DC2390_FIFO_ADCB_FIL       = 0x00000003
DC2390_FIFO_UP_DOWN_COUNT  = 0x00000004
DC2390_FIFO_FORMATTER_FILT = 0x00000005
DC2390_FIFO_FORMATTER_NYQ  = 0x00000006
DC2390_FIFO_CONS_HDEADBEEF = 0x00000007
 
# Number of samples to average in variable decimation mode. Can be redefined
# at top-level
LTC2500_N_FACTOR = 64

def LTC6954_sockit_reg_write(controller, base, cs_mask, addr, data):
    controller.sockit_reg_write(base | SPI_SS, cs_mask) # CS[0]
    controller.sockit_reg_write(base | SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(base | SPI_TXDATA, addr << 1) # LTC6954 Reg 0
    controller.sockit_reg_write(base | SPI_TXDATA, data)
    controller.sockit_reg_write(base | SPI_CONTROL, 0x00000000) #Raise CS

    
def LTC6954_configure(controller, divisor = 4):
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_TXDATA, 0x00) # LTC6954 Reg 0
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_TXDATA, 0x00)
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_CONTROL, 0x00000000) #Raise CS
    
    spistat = controller.sockit_reg_read(SPI_PORT_BASE | SPI_STATUS)
    #print ("SPI Status: " + str(spistat))
    

    # Register 1 controls the DAC clock outputs. The phase may need to be tweaked.
    # Try changing to 0x83 (delay by 3 200M clock cycles, equivalent to advancing by one.)
    #controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000000) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x02) # LTC6954 Reg 1
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x83)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    spistat = controller.sockit_reg_read(SPI_PORT_BASE | SPI_STATUS)
    #print ("SPI Status: " + str(spistat))
    
    #controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x04) # LTC6954 Reg 2
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, divisor)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x06) # LTC6954 Reg 3
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x80)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x08) # LTC6954 Reg 4
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, divisor)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x0A) # LTC6954 Reg 5
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x80)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x0C) # LTC6954 Reg 6
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, divisor)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    #print ("Sync pulse")
    #Issue SYNC pulse
    controller.sockit_reg_write(CONTROL_BASE, 0x00000010);
    sleep(0.1)
    controller.sockit_reg_write(CONTROL_BASE, 0x00000000);
    
    
def ramp_test(controller, recordlength, trigger = 0, timeout = 0.0):
#    print("Starting Capture system...\n");
    controller.sockit_reg_write(NUM_SAMPLES_BASE, recordlength)
    controller.sockit_reg_write(CONTROL_BASE, CW_START)
    sleep(0.1) #sleep for a second
    controller.sockit_reg_write(CONTROL_BASE, CW_EN_TRIG|CW_START)

# First, capture pattern data
    cap_start_time = time.time();
    ready = controller.sockit_reg_read(DATA_READY_BASE) # Check data ready signal
    while((ready & 0x01) == 1):
        ready = controller.sockit_reg_read(DATA_READY_BASE) # Check data ready signal
    cap_time = time.time() - cap_start_time
    print('ready signal is %d' % ready)
    print("After " + str(cap_time) + " Seconds...")
    if(cap_time > timeout):
        print("TIMED OUT!!")
    controller.sockit_reg_write(CONTROL_BASE, 0x0)
    stopaddress = controller.sockit_reg_read(BUFFER_ADDRESS_BASE)
    read_start_address = stopaddress - 4*recordlength
    if(read_start_address < 0):
        print("Original Memory starting address: %d" % read_start_address)
        read_start_address += 2**30
        print("Rolling over zero, let's see if we can deal with it!")
    print("Memory starting address: %d" % read_start_address)

# Calculate number of 1M blocks
    numblocks = 1
    if(recordlength >= 2**20):
        numblocks = recordlength / 2**20 # Separate into blocks of a megapoint
    print("Testing " + str(numblocks) + "blocks")

    errors = 0
    firstblock = True
    blocklength = recordlength / numblocks
    for blocknum in range (0, numblocks):
        print("Testing block " + str(blocknum))
    
    
    #    print('Reading a block...')
        block = controller.mem_read_block(read_start_address, blocklength)
        read_start_address += (4 * blocklength)
    #    dummy, block = controller.mem_read_block(stopaddress, NUM_SAMPLES) # Trying to find triggered data!!
        data = block#(ctypes.c_int * (blocklength)).from_buffer(bytearray(block))
        print('Got a %d byte block back' % len(block))
        print('First value: %d' % data[0])
        print(' Last value: %d' % data[blocklength - 1])
        if(firstblock == True):
            seed = data[0]
            firstblock = False
        for i in range (0, (recordlength / numblocks)):
            if(data[i] - 1 != seed):
                errors += 1
            seed = data[i]
    print("Pardon the Obi-One error, we'll fix it shortly... we promise.")
    return errors


# Okay, now let's try writing to the DAC lookup table remotely!
def load_arb_lookup_table(controller, data):
    cDataType = ctypes.c_uint * 65536
    cData     = cDataType()
    print("Writing downward ramp to LUT!")
    for i in range(0, 65536): 
        #cData[i] = (i << 16 | (65535 - i)) # Reverse ramp, useful for debug...
        point = int(data[i])
        if (point < 0):
            point += 65536
        cData[i] = (i << 16 | (point))
    
    controller.sockit_reg_write(CONTROL_BASE, 0x00000020) # Enable writing from blob side...
    controller.sockit_reg_write_LUT(LUT_ADDR_DATA_BASE, 65535, cData)
    controller.sockit_reg_write(CONTROL_BASE, 0x00000000) # Disable writing from blob side...
    print("Done writing to LUT! Hope it went okay!")


    
    
'''



def capture(controller, recordlength, trigger = 0, timeout = 0.0):
#    print("Starting Capture system...\n");
    controller.sockit_reg_write(NUM_SAMPLES_BASE, recordlength)
    controller.sockit_reg_write(CONTROL_BASE, CW_START)
    sleep(0.1) #sleep for a second
    controller.sockit_reg_write(CONTROL_BASE, CW_EN_TRIG|CW_START)
#    controller.sockit_reg_write(CONTROL_BASE, (CW_EN_TRIG)) # Drive trigger enable high, then low.

#    controller.sockit_reg_write(CONTROL_BASE, CW_START)
#    sleep(timeout) #sleep for a second
    cap_start_time = time.time();
    ready = controller.sockit_reg_read(DATA_READY_BASE) # Check data ready signal
    while((ready & 0x01) == 1):
        ready = controller.sockit_reg_read(DATA_READY_BASE) # Check data ready signal
    cap_time = time.time() - cap_start_time
    print('ready signal is %d' % ready)
    print("After " + str(cap_time) + " Seconds...")
    if(cap_time > timeout):
        print("TIMED OUT!!")
    controller.sockit_reg_write(CONTROL_BASE, 0x0)
#    print("Control system execution finished.\n")
#    print("Pulling START signal low.")

#    print("attempting to read stop address...")
    stopaddress = controller.sockit_reg_read(BUFFER_ADDRESS_BASE)
#    print("Ending address of ring buffer: " + str(stopaddress))
    read_start_address = stopaddress - 4*recordlength - 128*4
#    read_start_address = stopaddress - 16*NUM_SAMPLES # Trying to find triggered data!!
    
#    print("Are we still counting??")
#    sleep(1.0)
#    print("attempting to read stop address...")
#    stopaddress = controller.sockit_reg_read(BUFFER_ADDRESS_BASE)
#    print("Ending address of ring buffer: " + str(stopaddress))
#    read_start_address = stopaddress - NUM_SAMPLES
#    print("Apparently not. Let's capture for another second and see where we are...")    
#    controller.sockit_reg_write(CONTROL_BASE, CHANNEL | 0x00000001);
#    sleep(1.0) #Collect a second worth of data
#    controller.sockit_reg_write(CONTROL_BASE, CHANNEL | 0);
#    newaddress = controller.sockit_reg_read(BUFFER_ADDRESS_BASE)
#    print("went this many samples further:" + str(newaddress - stopaddress))

#    print('Reading a block...')
    print 'Starting address: '
    print read_start_address
    block = controller.mem_read_block(read_start_address, recordlength)
#    dummy, block = controller.mem_read_block(stopaddress, NUM_SAMPLES) # Trying to find triggered data!!
#    data = (ctypes.c_int * recordlength).from_buffer(bytearray(block))
#    print('Got a %d byte block back' % len(block))
#    print('first 16 values:')
#    for j in range(0, 16):
#        print('value %d' % data[j])
#    print('and the last value: %d' % data[recordlength - 1])
    
    return block#data

## A handy function to turn unsigned values from mem_read_block to signed
## 32-bit values
#def uns32_to_signed32(data):
#    for i in range(0, len(data)):    
#        if(data[i] > 0x7FFFFFFF):
#            data[i] -= 0xFFFFFFFF
#    return data



def LTC6954_configure_default(controller):
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_TXDATA, 0x00) # LTC6954 Reg 0
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_TXDATA, 0x00)
    controller.sockit_reg_write(SPI_PORT_BASE | SPI_CONTROL, 0x00000000) #Raise CS
    
    spistat = controller.sockit_reg_read(SPI_PORT_BASE | SPI_STATUS)
    print ("SPI Status: " + str(spistat))
    

    # Register 1 controls the DAC clock outputs. The phase may need to be tweaked.
    # Try changing to 0x83 (delay by 3 200M clock cycles, equivalent to advancing by one.)
    #controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000000) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x02) # LTC6954 Reg 1
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x83)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    spistat = controller.sockit_reg_read(SPI_PORT_BASE | SPI_STATUS)
    print ("SPI Status: " + str(spistat))
    
    #controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x04) # LTC6954 Reg 2
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x04)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x06) # LTC6954 Reg 3
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x80)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x08) # LTC6954 Reg 4
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x04)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x0A) # LTC6954 Reg 5
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x80)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_SS, 0x00000001) # CS[0]
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000400) # Drop CS
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x0C) # LTC6954 Reg 6
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_TXDATA, 0x04)
    controller.sockit_reg_write(SPI_PORT_BASE + SPI_CONTROL, 0x00000000) #Raise CS
    
    print ("Sync pulse")
    #Issue SYNC pulse
    controller.sockit_reg_write(CONTROL_BASE, 0x00000010);
    sleep(0.1)
    controller.sockit_reg_write(CONTROL_BASE, 0x00000000);




'''



    