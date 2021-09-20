# Copyright (C) 2021 Analog Devices, Inc.
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
import matplotlib.pyplot as plt
from adi import ad7768
from time import sleep

hardcoded_ip = 'ip:analog.local'
print("args:\n", sys.argv)
my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip

# Brute force for now. Set up lists for each test you want to run.
# There also appears to be a subtlety with power modes and sample rates; the driver
# may not gracefully handle asking for a power mode that isn't supported by the particular sample rate.
# Available Sample Rates: [1000, 2000, 4000, 8000,16000,32000,64000,128000,256000]
tests_sample_rates =    [1000, 2000, 4000, 8000, 16000,32000, 64000, 128000,256000]
tests_capture_lengths = [256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536 ]
tests_power_modes =    ["LOW_POWER_MODE", "LOW_POWER_MODE", "MEDIAN_MODE", "MEDIAN_MODE",
                         "FAST_MODE", "FAST_MODE", "FAST_MODE", "FAST_MODE", "FAST_MODE"]

#tests_power_modes = ["FAST_MODE"]* len(tests_sample_rates)
tests_filter_modes =     ["WIDEBAND"] * len(tests_sample_rates)


adc = ad7768(uri=my_ip)
#adc.sample_rate = 8000
#adc.rx_buffer_size = 1024
#adc.power_mode = "FAST_MODE"
#adc.filter = "WIDEBAND"

for i in range(len(tests_sample_rates)):
    print("Test Number ", i)
    print("Sample Rate: ", tests_sample_rates[i])
    print("Capture Length: ", tests_capture_lengths[i])
    print("Filter Mode: ", tests_filter_modes[i])
    print("Power Mode: ", tests_power_modes[i])

    adc.sample_rate = tests_sample_rates[i]
    adc.power_mode = tests_power_modes[i]


    adc.filter = tests_filter_modes[i]
    adc.rx_buffer_size = tests_capture_lengths[i]
    sleep(0.25)
    data = adc.rx()
    adc.rx_destroy_buffer()


    print('Writing data to file...\n')
    fname = ("csv_files\cn0501_test_" + str(tests_sample_rates[i]) + "_" +
             str(tests_capture_lengths[i]) + "_" + tests_filter_modes[i] +
             "_" + tests_power_modes[i] + ".csv")
    with open(fname, 'w') as f:
        for i in range (0, len(data[0])-1):
            f.write(str(data[0][i]) + "," + str(data[1][i]) + "," +
                    str(data[2][i]) + "," + str(data[3][i]) + "," +
                    str(data[4][i]) + "," + str(data[5][i]) + "," +
                    str(data[6][i]) + "," + str(data[7][i]) + "," + '\n')


plt.clf()
plt.ylim((-5,5))

for ch in adc.rx_enabled_channels:
        plt.plot(range(0, adc.rx_buffer_size), data[ch],
                 label = "voltage" + str(ch))
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=2, mode="expand", borderaxespad=0.)
plt.pause(0.01)

#del adc

