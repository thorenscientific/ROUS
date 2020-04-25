# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Copyright (c) 2016-2019 Analog Devices, Inc. All rights reserved.
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
        The purpose of this module is to create the packets for the SPI to
        Avalon MM bus.
"""

# Global constants
CONST_SEQUENTIAL_WRITE = 0x04
CONST_SEQUENTIAL_READ = 0x14
CONST_NON_SEQUENTIAL_WRITE = 0x00
CONST_NON_SEQUENTIAL_READ = 0x10

CONST_HEADER_LEN = 8
CONST_REPONSE_LEN = 4

CONST_SOP = 0x7A
CONST_EOP = 0x7B
CONST_CHANNEL = 0x7C
CONST_ESC = 0x7D

CONST_BYTES_IDLE_CHAR = 0x4A
CONST_BYTES_ESC_CHAR = 0x4D

# Creates the packet for a read and write
def create_packet(trans_type, size, address, data = None):
    # Setup header from address
    header = [trans_type, 0, (size>>8)& 0xFF, size & 0xFF,(address>>24) & 0xFF,
            (address>>16) & 0xFF, (address>>8) & 0xFF, address & 0xFF]
    
    temp_header = []
    
    for x in range(0, 8):
        if int(header[x]) == CONST_CHANNEL:
            temp_header.append(CONST_ESC)
            temp_header.append(int(CONST_CHANNEL) ^ 0x20)
        elif int(header[x]) == CONST_ESC:
            temp_header.append(CONST_ESC)
            temp_header.append(int(CONST_ESC) ^ 0x20)
        elif int(header[x]) == CONST_SOP:
            temp_header.append(CONST_ESC)
            temp_header.append(int(CONST_SOP) ^ 0x20)
        elif int(header[x]) == CONST_EOP:
            temp_header.append(CONST_ESC)
            temp_header.append(int(CONST_EOP) ^ 0x20)
        else:
            temp_header.append(header[x])
    
    header = temp_header
    if data is None:
        pass # Do nothing
    else:
        # Add the data to the header
        for x in range(0, size):
            # Insert ESC bytes to all cases and XOR data 
            if(int(data[x]) == CONST_ESC):
                header.append(CONST_ESC)
                header.append(int(data[x]) ^ 0x20)
            elif(int(data[x]) == CONST_SOP):
                header.append(CONST_ESC)
                header.append(int(data[x]) ^ 0x20)
            elif(int(data[x]) == CONST_EOP):
                header.append(CONST_ESC)
                header.append(int(data[x]) ^ 0x20)
            elif(int(data[x]) == CONST_CHANNEL):
                header.append(CONST_ESC)
                header.append(int(data[x]) ^ 0x20)
            else:   
                header.append(int(data[x]) & 0xFF)

    # Build the packet
    packet = [CONST_SOP, CONST_CHANNEL, 0 ]
    
    # Add the header
    packet += header 
    
    # Insert the EOP byte
    if packet[len(packet)-2] == CONST_ESC:
        packet.insert(len(packet)-2, CONST_EOP)
    else:
        packet.insert(len(packet)-1, CONST_EOP)

    x = 0
    # Insert ESC characters to all cases and XOR data
    while len(packet) > x:
        if (packet[x] == CONST_BYTES_ESC_CHAR):
            temp = packet[x]
            packet[x] = CONST_BYTES_ESC_CHAR
            packet.insert(x+1, temp ^ 0x20)
        if (packet[x] == CONST_BYTES_IDLE_CHAR):
            temp = packet[x]
            packet[x] = CONST_BYTES_ESC_CHAR
            packet.insert(x+1, temp ^ 0x20)
        x += 1
    return packet

# Converts the packets to DC590 string
def packet_to_DC590(packet, read_bytes):
    # Create 590 String
    dc590_string = ""
    
    # Insert SPI characters for the DC590
    for x in range(0,len(packet)):
        dc590_string += "S" + hex(packet[x])
        if packet[x] < 0x10:
            dc590_string = dc590_string.replace('x', '')
        else:
            dc590_string = dc590_string.replace('0x', '')
    # Insert read charters 
    if read_bytes > 0:
        for x in range(0,2*read_bytes + 4):
            dc590_string += 'R'
        
    # Insert CS Low and High characters. Also, ensure all HEX characters are capitalized
    dc590_string = 'x'+ dc590_string.upper() + 'X'
    
    return dc590_string # Return the string

# Converts DC590 string to list packets
def DC590_to_packet(string):
    # Create a list
    packet = [];
    
    # Convert the string to list 
    for x in range(0, len(string), 2):
        try:
            packet.append((int(string[x],16)<<4) + (int(string[x+1],16)))
        except:
            packet.append((int(string[x],16)))
    return packet

# Converts the packet to data list     
def packet_to_data(packet):
    
    x = 0
    # Remove the IDLE and ESC characters to all cases and XOR data
    while len(packet) > x:
        if (packet[x] == CONST_BYTES_IDLE_CHAR):
            packet.pop(x)
            x -= 1
        elif (packet[x] == CONST_BYTES_ESC_CHAR):
            packet.pop(x)
            packet[x] = packet[x] ^ 0x20
        x += 1
    # Remove the SOP, EOP, Channel, and ESC bytes to all cases and XOR data 
    x = 0 
    while len(packet) > x:
        if (packet[x] == CONST_CHANNEL):
            packet.pop(x)
            packet.pop(x)
            x -= 1
        elif (packet[x] == CONST_SOP) or (packet[x] == CONST_EOP):
            packet.pop(x)
            x -= 1
        elif (packet[x] == CONST_ESC):
            packet.pop(x)
            packet[x] = packet[x] ^ 0x20 
        x += 1
    if len(packet) == 0:
        return [0, 0, 0, 0, 0, 0, 0, 0]
    return packet

if __name__ == "__main__":
    pass