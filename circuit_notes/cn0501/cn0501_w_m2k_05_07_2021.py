# Copyright (C) 2020 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTIT11111111111111111111111111111111111111111111111111111111111111111111UTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
print("Program start")

import math
import pandas as pd
import time
from scipy.signal import periodogram,find_peaks,ricker
import matplotlib.pyplot as plt
import numpy as np
import os
print("Python Packages Import done")

from adi import ad7768
import libm2k
print("ADI Packages Import done")

import m2k_ricker_wav 


loops = 0
ch = 0
nsecs=0
fname = ""

cwd = os.getcwd()
fpath = cwd + "\examples\cn0501\csv_files\\"
print ("Filepath: " + fpath)

def test_param():
    #GEOPHONE A0:A1:A2
    #ADXL A4:A5:A6
    global loops,ch,fname,nsecs

    #print("\nHow many loops?")
    loops = 1
    #print("\nWhat channel?")
    ch = 0

    #print("\n # Seconds record")
    nsecs = 2 

    #print("\nExport filename?")
    fname = "ch"+str(ch)
   

def cn0501(): 
    srate = [8000,16000,32000,64000,128000,256000]

    for sps in srate:
        adc = ad7768(uri="ip:169.254.92.202")
        adc.power_mode = "FAST_MODE" #FAST_MODE MEDIAN_MODE LOW_POWER_MODE
        adc.filter = "SINC5"
        adc.sample_rate = sps 
        adc.rx_buffer_size = int(sps*2) #max 512000
    
        #print("Sample Rate")
        #print(adc.sample_rate)

        #print("Buffer Size")
        #print(adc.rx_buffer_size)

        #print("Kernel Buffers Count")
        #print(adc.get_kernel_buffers_count)

        #print("Enabled Channels")
        #print (adc.rx_enabled_channels)
        
        #sec_rec = math.ceil(adc.sample_rate/adc.rx_buffer_size)*nsecs #use if 1 sec worth of record
        sec_rec = math.ceil(adc.sample_rate/adc.rx_buffer_size) #use for n sec worth


        print("\nSTART RECORD\n")
        for nloop in range(0,loops):
            #print(nloop)
            vdata = []
            count = 0
            dt = []
            start = time.time()
            for _ in range(int(sec_rec)):
                    #dstart = time.time()    ####
                    data = adc.rx()         #TRANSACTION
                    #dend = time.time()      ####
                    vdata.append(data[ch])  
                    #dt.append(dend-dstart)  ####
                    count += len(data[ch])
            end = time.time()
            rec_time = (end - start)
            
            #print("Sample rate:   " + str(srate[0]) +"sps")
            #print("Buffer length:   " + str(adc.rx_buffer_size) +"")
            #print("No. of buffers:   " + str(sec_rec) +"")
            print("Total Elapsed:   " + str(rec_time) +"s")
            #print("adc.rx() Elapsed: " + str(np.sum(dt)) +"s")
            #print("Average adc.rx() Elapsed: " + str(np.mean(dt)) +"s")
            #print("others Elapsed: " + str(rec_time-np.sum(dt)) +"s")

            vdata_arr = np.asarray(vdata)
            vdata_arr = vdata_arr.reshape(count,1)

            DF = pd.DataFrame(vdata_arr)
            #f = fname + "_loop" + str(nloop)+"_sps"+str(sps)+"_buffer"+str(int(adc.rx_buffer_size))+".csv"
            f = fname + "_loop" + str(nloop)+"_sps"+str(sps)+"_5vpp"+".csv"

            #File directory of exported csv files 
            DF.to_csv(fpath+f, index = False, header = False)

        
        print("Export done")

def main():
    test_param()
    m2k_ricker_wav.wavdiff_out()
    #m2k_ricker_wav.wavsingle_out()
    cn0501()
    m2k_ricker_wav.wav_close()

main()

'''
'''

