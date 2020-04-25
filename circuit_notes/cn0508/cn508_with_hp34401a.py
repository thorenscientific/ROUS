#!/usr/bin/python

import sys
import numpy as np
import time

import visa
from llt.utils.hp_multimeters import *


rm = resource_manager()
hp34401a = rm.open_resource("GPIB0::22::INSTR", timeout = 5000)


try:
    import iio
except:
    print("libiio bindings not found in paths, looking in ~/libiio")
    sys.path.append('~/libiio/bindings/python')
    import iio

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
    #ctx = iio.Context('local:') # "local" is what you would use if you were running this script directly on the Raspberry Pi.
                                 # To run over a network connection, run iiod on the Pi, then give the Pi's address as shown next...
    ctx = iio.Context(my_ip)
    adc = ctx.find_device("ad7124-4") # Pretty self explanatory. Locate the devices and their associated channels.
    dac = ctx.find_device("ad5683r") # Often there's a bit of investigation to do here if you're not very familiar with the driver.
    print("setting up DAC, setting output to 2.5V...")
    dac_op = dac.find_channel("voltage0", is_output=True) # Defaults to False!! Set true for DACs.
    dac_op.attrs['raw'].value = '11000'#'5958' # Hardcoded value, dependent on CN0508 op-amp gain
    dac_scale = float(dac_op.attrs['scale'].value) # This is set by the device tree, it's not an actual measured value.
    print("DAC scale factor: " + str(dac_scale))

    print("finding ADC channels...")
    ch0 = adc.find_channel("voltage0-voltage19")
    ch1 = adc.find_channel("voltage1-voltage19")
    ch2 = adc.find_channel("voltage2-voltage19")
    ch3 = adc.find_channel("voltage3-voltage19")
    ch4 = adc.find_channel("voltage4-voltage19")
    ch5 = adc.find_channel("voltage5-voltage19")
    ch6 = adc.find_channel("voltage6-voltage19")
    ch7 = adc.find_channel("voltage7-voltage19")

    print("Setting sample rates...")
    #Set maximum sampling frequency
    ch0.attrs['sampling_frequency'].value = '9600'
    ch1.attrs['sampling_frequency'].value = '9600'
    ch2.attrs['sampling_frequency'].value = '9600'
    ch3.attrs['sampling_frequency'].value = '9600'
    ch4.attrs['sampling_frequency'].value = '9600'
    ch5.attrs['sampling_frequency'].value = '9600'
    ch6.attrs['sampling_frequency'].value = '9600'
    ch7.attrs['sampling_frequency'].value = '9600'

    print("Setting scales to 0.000149011 (unity gain)...")
    ch0.attrs['scale'].value = str(adc_scale)
    ch1.attrs['scale'].value = str(adc_scale)
    ch2.attrs['scale'].value = str(adc_scale)
    ch3.attrs['scale'].value = str(adc_scale)
    ch4.attrs['scale'].value = str(adc_scale)
    ch5.attrs['scale'].value = str(adc_scale)
    ch6.attrs['scale'].value = str(adc_scale)
    ch7.attrs['scale'].value = str(adc_scale)
    print("Reading all raw voltages...\n\n")

    v0 = float(ch0.attrs['raw'].value) * adc_scale
    v1 = float(ch1.attrs['raw'].value) * adc_scale
    v2 = float(ch2.attrs['raw'].value) * adc_scale
    v3 = float(ch3.attrs['raw'].value) * adc_scale
    v4 = float(ch4.attrs['raw'].value) * adc_scale
    v5 = float(ch5.attrs['raw'].value) * adc_scale
    v6 = float(ch6.attrs['raw'].value) * adc_scale
    v7 = float(ch7.attrs['raw'].value) * adc_scale #not used.

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
            dac_op.attrs['raw'].value = str(int(setpoint * 1000.0 / (11.0 *dac_scale)))
            time.sleep(0.5) #This is fine as long as you're not wainting for thermal equilibrium.
            # Read voltages again
            v0 = float(ch0.attrs['raw'].value) * adc_scale
            v1 = float(ch1.attrs['raw'].value) * adc_scale
            v2 = float(ch2.attrs['raw'].value) * adc_scale
            v4 = float(ch4.attrs['raw'].value) * adc_scale
            readback = hp34401a_read_voltage(hp34401a)

            ldoU2_temp = v0 * ldoU2_temp_scale
            ldoU3_temp = v1 * ldoU3_temp_scale
            iout = v2 * iout_scale
            vout = v4 * vout_scale
            print(str(setpoint) + "," + str(ldoU2_temp) + "," + str(ldoU3_temp)
                  + "," + str(iout) + "," + str(vout) + ","+ str(readback))
    print("Setting DAC output to zero, just to be safe...")
    dac_op.attrs['raw'].value = "0"

    del ctx # Delete context


if __name__ == '__main__':
    import sys
    hardcoded_ip = 'ip:10.26.148.148' #118
    my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip


    testdata = main(my_ip)