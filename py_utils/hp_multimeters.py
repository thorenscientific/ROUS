# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Copyright (c) 2015-2019 Analog Devices, Inc. All rights reserved.
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

import visa

def hp34401a_lcd_disp(hp_meter, message):
    """Displays up to 12 charaters on the hp33401a
       hp_meter: the instance of the meter
       message: the 12 charaters to be displayed on the meter
    """
    hp_meter.write("DISP:TEXT:CLE")
    hp_meter.write("DISP:TEXT '" + str(message) + "'")

def hp34401a_read_voltage(hp_meter):
    """Measures voltage in auto range and auto resolution
       returns the voltage in float
       hp_meter: the instance of the meter
    """
    hp_meter.write("MEAS:VOLT:DC? DEF,DEF")    
    return float(hp_meter.read())

def hp34401a_read_voltage_rng_res(hp_meter , v_range, v_resolution):
    """Measures voltage with specified range and resolution
       returns the voltage in float
       hp_meter: the instance of the meter
       v_range: the desired voltage range
       v_resolution: the desired resolution
    """
    hp_meter.write("MEAS:VOLT:DC? " + str(v_range) + " , " + str(v_resolution))
    return float(hp_meter.read())


def hp3458a_lcd_disp(hp_meter, message):
    """Displays up to 16 charaters on the hp2458a
       hp_meter: the instance of the meter
       message: the 16 charaters to be displayed on the meter
    """
    hp_meter.write("DISP 3")
    hp_meter.write("DISP 2 '" + str(message) + "'")
    
def hp3458a_self_test(hp_meter):
    """Starts a self test
       hp_meter: the instance of the meter
    """
    hp_meter.write("TEST")
    
def hp3458a_init(hp_meter):
    """Initializes the meter to DC voltage measurment in the 10V range
       hp_meter: the instance of the meter
    """
    hp_meter.write("RESET")
    hp_meter.write("TARM HOLD")
    hp_meter.write("FUNC DCV") # Set to DC voltage measurment 
    hp_meter.write("RANGE 10") # Set to 10V range
    hp_meter.write("LFREQ LINE") # Measure line freq and set rejection filter
    hp_meter.write("NPLC 1")
    hp_meter.write("AZERO ONCE")
    hp_meter.write("FIXEDZ ON") # Fixed input impedance 
    
def hp3458a_read_voltage(hp_meter):
    """Measures voltage
       returns the voltage in float
       hp_meter: the instance of the meter
    """
    hp_meter.write("TARM SGL")
    return float(hp_meter.read())

def resource_manager():
    """Connect to the resource manager
       returns the visa avalable resources
    """
    return visa.ResourceManager()
    
if __name__ == "__main__":
    # Connect to test equipment
    # ---------------------------------------------------------------------
    
    # Connect to visa resource manager
    rm = resource_manager()
    
    try:
        # Connect to the HP multimeter
        hp3458a = rm.open_resource("GPIB0::22::INSTR", 
                                   read_termination = "\r\n", 
                                   timeout = 50000)
        print hp3458a
        hp3458a_init(hp3458a)
        hp3458a_lcd_disp(hp3458a, "WooHoo!")
        v = hp3458a_read_voltage(hp3458a)
        print v
        
        
    finally:
        hp3458a.close()