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

"""
    Description:
        The purpose of this module is to find and connect to Linear
        Technology's Linduino. The DC590 enhanced sketch.
"""
###############################################################################
# Libraries
###############################################################################
import time
import serial
from serial.tools.list_ports import comports

def get_available_ports():
    return [str(c[0]) for c in comports()]

# Open a serial connection with Linduino
class Linduino:
     
    def __init__(self):
        self.open()
        
    def __del__(self):
        self.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, a, b, c):
        self.close()

    def open(self):
        print "\nLooking for COM ports ..."
        ports = get_available_ports()
        print "Available ports: " + str(ports) + "\n"
        print "Looking for Linduino ..." 
        for port in ports:
            try:
                testser = serial.Serial(port, 115200, timeout = 0.5) 
            except:
                continue
            
            time.sleep(2)   # A delay is needed for the Linduino to reset

            try:
                id_linduino = testser.read(50) # Remove the hello from buffer

                # Get ID string
                testser.write("i") 
                id_linduino = testser.read(50)
                if id_linduino[20:25] == "DC590":
                    Linduino = port
            except:
                continue
            finally:
                testser.close()
        
        try:
            # Open serial port
            self.port = serial.Serial(Linduino, 115200, timeout = 0.05)
            time.sleep(2)       # A delay is needed for the Linduino to reset
            self.port.read(50)  # Remove the hello from buffer
            print "    Found Linduino!!!!"
        except:
            print "    Linduino was not detected"
        
    def close(self):
        try:
            self.port.close()  # Close serial port
            return 1
        except Exception:
            return 0
            
    def transfer_packets(self, send_packet, return_size = 0):
        try:
            if len(send_packet) > 0:
                self.port.write(send_packet)                       # Send packet
            if return_size > 0:            
                return self.port.read(return_size) # Receive packet
            else:
                return None # return_size of 0 implies send only
        except:
            return 0

###############################################################################
# Function Tests
###############################################################################

if __name__ == "__main__":
    
    
    try:
        linduino = Linduino() # Look for the DC590

        linduino.port.write('i')
        print "\n" + linduino.port.read(50)
        
    finally:
        linduino.close()

    print "Test Complete"  