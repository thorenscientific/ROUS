# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 07:21:55 2019

@author: MThoren
"""
from time import sleep
import sys
try:
    import adi
    sleep(0.5)
except:
    print ("pyadi-iio not found!")
    sys.exit(0)

buflen = 8

try:
    myadc = adi.ad7124(uri="ip:10.26.148.148", part="ad7124-4")
    mydac = adi.ad5683r(uri="ip:10.26.148.148")
except:
    print("No device found")
    sys.exit(0)


sc = myadc.scale_available
myadc.channel[0].scale = sc[2]
myadc.rx_output_type='SI'

myadc.sample_rate = 19200 # sets sample rate for all channels
myadc.rx_enabled_channels = [ 0 ] # currently only one enabled channel buffer works at a time
myadc.rx_buffer_size = 100

raw = myadc.channel[0].raw
data = myadc.rx()

print(data)

volt_data = myadc.to_volts(0, data)
volt_raw = myadc.to_volts(0, data[0])




del myadc
del mydac
