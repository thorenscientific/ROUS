#!/usr/bin/python
# Copyright (C) 2019 Analog Devices, Inc.
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
# RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import numpy as np
import time
import adi

# Channel scale factors
adc_scale = 0.000149011
ldoU2_temp_scale = 1.0 # Degrees C/mV
ldoU3_temp_scale = 1.0 # Degrees C/mV
iout_scale = 0.005 # A/mV
vin_scale =  14.33/1000 # V/mV
vout_scale =  10.52/1000 # V/mV
ilim_pos_scale =  100.0/(2.5*1000) # Percent
vpot_pos_scale =  100.0/(2.5*1000) # Percent

def main(my_ip):
    try:
        myadc = adi.ad7124(uri=my_ip)
        mydac = adi.ad5686(uri=my_ip)
    except:
      print("No device found")
      sys.exit(0)

    print("setting up DAC, setting output to 2.5V...")
    mydac.channel[0].raw = '11000'#'5958' # Hardcoded value, dependent on CN0508 op-amp gain
    dac_scale = mydac.channel[0].scale # This is set by the device tree, it's not an actual measured value.
    print("DAC scale factor: " + str(dac_scale))

    print("Setting sample rates...")
    #Set maximum sampling frequency
    myadc.sample_rate = 9600

    print("Setting scales to 0.000149011 (unity gain)...")
    for i in range(0, 8):
      myadc.channel[0].scale = 0.000149011

    print("Reading all raw voltages...\n\n")

    v0 = float(myadc.channel[0].raw) * adc_scale
    v1 = float(myadc.channel[1].raw) * adc_scale
    v2 = float(myadc.channel[2].raw) * adc_scale
    v3 = float(myadc.channel[3].raw) * adc_scale
    v4 = float(myadc.channel[4].raw) * adc_scale
    v5 = float(myadc.channel[5].raw) * adc_scale
    v6 = float(myadc.channel[6].raw) * adc_scale
    v7 = float(myadc.channel[7].raw) * adc_scale #not used.

    #Calculate parameters
    ldoU2_temp = v0 * ldoU2_temp_scale
    ldoU3_temp = v1 * ldoU3_temp_scale
    iout = v2 * iout_scale
    vin = v3 * vin_scale
    vout = v4 * vout_scale
    ilim_pos = v5 * ilim_pos_scale
    vpot_pos = v6 * vpot_pos_scale

    print("Board conditions:")
    print("U2 Temperature: " + str(ldoU2_temp) + " C")
    print("U3 Temperature: " + str(ldoU3_temp) + " C")
    print("Output Current: " + str(iout) + " A")
    print("Input Voltage: " + str(vin) + " V")
    print("Output Voltage: " + str(vout) + " V")
    print("ILIM pot position: " + str(ilim_pos) + " %")
    print("Vout pot position: " + str(vpot_pos) + " V")

    print("Starting sweep!")
    for load in range(1): #Here is where you would step the loading conditions
        # Trisha, hers is where you would set the electronic load.
        # Start with a resistive load, and note that there might be a minimum voltage required
        # so when you're setting np.arange, start at something higher than zero (maybe 1V?)
        print("Data for load condition " + str(load) + ":")
        print("Vout setpoint,U2 Temperature,U3 temperature,output current,output voltage")
        for setpoint in np.arange(0.0, 15.0, 0.5):
            mydac.channel[0].raw = str(int(setpoint * 1000.0 / (11.0 *dac_scale)))
            time.sleep(0.5) #This is fine as long as you're not wainting for thermal equilibrium.
            # Read voltages again
            v0 = float(myadc.channel[0].raw) * adc_scale
            v1 = float(myadc.channel[1].raw) * adc_scale
            v2 = float(myadc.channel[2].raw) * adc_scale
            v4 = float(myadc.channel[4].raw) * adc_scale

            ldoU2_temp = v0 * ldoU2_temp_scale
            ldoU3_temp = v1 * ldoU3_temp_scale
            iout = v2 * iout_scale
            vout = v4 * vout_scale
            print(str(setpoint) + "," + str(ldoU2_temp) + "," + str(ldoU3_temp) + "," + str(iout) + "," + str(vout))
    print("Setting DAC output to zero, just to be safe...")
    mydac.channel[0].raw = "0"

    del myadc
    del mydac


if __name__ == '__main__':
    hardcoded_ip = 'ip:10.26.148.148' #118
    my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip


    testdata = main(my_ip)