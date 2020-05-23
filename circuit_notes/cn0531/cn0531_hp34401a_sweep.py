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
from time import sleep
from ROUS.py_utils.hp_multimeters import *

#Either un-comment an ip address, or pass ip address as a command line argument
hardcoded_ip = 'ip:10.26.148.171'
#hardcoded_ip = 'ip:localhost'
my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip
print("Connecting with context at %s" % (my_ip))

try:
    import adi
    mydac = adi.ad5791(uri=my_ip) # REMEMBER TO VERIFY POWERDOWN/UP BEHAVIOR
except:
  print("No device found")
try:
    rm = resource_manager()
    hp34401a = rm.open_resource("GPIB0::22::INSTR", timeout = 5000)
except:
    print("Something went wrong... did you install visa? (NOTpyvisa?)")

print("setting up DAC, setting output to 0.0V...")
dac_scale = mydac.channel[0].scale # This is set by the device tree, it's not an actual measured value.
print("DAC scale factor: " + str(dac_scale))
for i in range(0,6):
    print("setting DAC to %f volts" % (i * 0.4999))
    mydac.channel[0].volts = (i * 0.4999)
    sleep(0.1)
    readback = hp34401a_read_voltage(hp34401a)
    print("meter: %f" % (readback))
    sleep(1.0)

del rm
print("Done!")
