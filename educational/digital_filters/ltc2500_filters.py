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
LTC2500_filters.py

This script imports the LTC2500-32 digital filter coefficents and plots the
impulse responses of the flat passband filters, and various combinations of
the frequency responses.

Tested with Python 2.7, Anaconda distribution available from Continuum Analytics,
http://www.continuum.io/
'''

# Import standard libraries
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
import time

# Import Linear Lab Tools utility funcitons
import sys
from DC2390_functions import * # Has filter DF, type information
import linear_lab_tools_functions as lltf


start_time = time.time();

# List of DF information - see DC2390_functions module
DF_list = [DF4, DF8, DF16, DF32, DF64, DF128, DF256, DF512, DF1k, DF2k, DF4k, DF8k, DF16k]
# List of filter type information
FT_list = [FTSINC1, FTSINC2, FTSINC3, FTSINC4, FTSSINC, FT_FLAT]

FS = 1000000 # Sample rate, for scaling horizontal frequency axis


# Read all filter coefficients into a big 2-d list, calculate corresponding
# magnitude responses, responses in dB. For each of these, the first index
# is the filter type (SINC2, SINC2, SSINC, Flat, etc.),
# the second index represents the DF. For example:
# filters[filter type][downsample factor][tap value]

# Reading files and doing these calculations takes a while. Only need to do once
# if you leave the console open.

try:
    read_files # See if defined
except: # if not, read files
    read_files = True

# read_files = False

if read_files == True:
    filters          = [[[] for j in range(len(DF_list))] for i in range(len(FT_list))]
    filt_resp_mag    = [[[] for j in range(len(DF_list))] for i in range(len(FT_list))]
    filt_resp_mag_db = [[[] for j in range(len(DF_list))] for i in range(len(FT_list))]
    ftnum = 0 # Handy numerical index
    for ft in FT_list:
        dfnum = 0 # Handy numerical index
        for df in DF_list:
            filename = "./ltc25xx_filters/" + ft.FT_txt + "_" + df.DF_txt + ".txt" # Construct filename
            filelength = lltf.linecount(filename) # Find out how long it is
            filters[ftnum][dfnum] = np.ndarray(filelength, dtype=float) # Add entry to list
            print(("reading " + str(filelength) + " coefficients from file " + filename))
            with open(filename, 'r') as infile: # Read in coefficients from files
                for i in range(0, filelength):
                    instring = infile.readline()
                    filters[ftnum][dfnum][i] = float(instring)
            filters[ftnum][dfnum] /= sum(filters[ftnum][dfnum]) # Normalize to unity gain
            filt_resp_mag[ftnum][dfnum] = lltf.freqz_by_fft_numpoints(filters[ftnum][dfnum], 2 ** 20) # Calculate magnitude response
            filt_resp_mag_db[ftnum][dfnum] = 20*np.log10(abs(filt_resp_mag[ftnum][dfnum])) # Calculate response in dB
            dfnum += 1
        ftnum += 1
    print(("Done reading in all coefficient files and calculating responses!!"))

# read_files = False # So that we don't re-read files if run again.

# Create filter response of Variable-SINC filter, N=2, to represent the simplest possible filter.
# (This mode is distinct from the other filters, it doesn't have a coefficient file.)
vsinc2 = np.ones(2) # Yup, that's it... just a couple of 1s!
vsinc2 /= sum(vsinc2) # Normalize to unity gain
vsinc_resp_mag = lltf.freqz_by_fft_numpoints(vsinc2, 2 ** 20) # Calculate magnitude response
vsinc_resp_mag_db = 20*np.log10(abs(vsinc_resp_mag)) # Calculate response in dB

fignum = 1 # Keep track of which figure we're on

# Plot the impulse responses on the same horizontal axis, with normalized
# amplitude for a better visual picture...
plt.figure(fignum)
plt.cla()
plt.ion()
ftnum = 5 # SSINC + Flattening
plt.title("Impulse response of SSINC+Flat filters")
for df in range(0, len(DF_list)):
    plt.plot(filters[ftnum][df] / max(filters[5][df]))
plt.xlabel("tap number")
plt.show()

fignum += 1

# Make vector of frequencies to plot / save against
haxis = np.linspace(0.0, FS, 2**20) # Horizontal axis

color_list = ["red","orange", "green", "blue", "purple", "black"]

# Plot frequency response, linear frequency axis
lw = 1.5 # Slightly thicker than default
dfnum = 6 # DF256
plt.figure(fignum)
plt.cla()
#plt.cla()
plt.title("LTC2500-32 filter responses (DF " + DF_list[dfnum].DF_txt + ")")
plt.xlabel('Frequency (Hz)')
plt.ylabel('Rejection (dB)')
#plt.axis([0, 16400, -100, 10])
plt.axis([20, 500000, -100, 5])
# All DF256 filters, for section of video comparing all filter types
plt.semilogx(haxis, filt_resp_mag_db[0][dfnum], linewidth=lw, color="red", zorder=1)
plt.semilogx(haxis, filt_resp_mag_db[1][dfnum], linewidth=lw, color="orange",  zorder=1)
plt.semilogx(haxis, filt_resp_mag_db[2][dfnum], linewidth=lw, color="green",  zorder=1)
plt.semilogx(haxis, filt_resp_mag_db[3][dfnum], linewidth=lw, color="blue",  zorder=1)
plt.semilogx(haxis, filt_resp_mag_db[4][dfnum], linewidth=lw, color="purple",  zorder=1)
plt.semilogx(haxis, filt_resp_mag_db[5][dfnum], linewidth=lw, color="black", zorder=1)

fignum += 1

# Selection of filters for section of video discussing versatility, compared
# with delta sigma
all_filter_plot = True
if all_filter_plot == True:
    plt.figure(fignum)
    plt.title("A wide selection of LTC2500-32 filter responses")
    plt.semilogx(haxis, vsinc_resp_mag_db, linewidth=lw, color="red", zorder=1) # Simple average of 2 points
    plt.semilogx(haxis, filt_resp_mag_db[5][6], linewidth=lw, color="black", zorder=1) # Example flat passband filter

    for dfnum in [0, 2, 4, 6, 8, 10]: # Not plotting all. If you do, the plot gets VERY dense!
        # For the SINC1 filters, don't plot all points. Once again, things get very dense if you do.
        plt.semilogx(haxis[0:2**(24-dfnum)], filt_resp_mag_db[0][dfnum][0:2**(24-dfnum)], linewidth=lw, color="red", zorder=1) # Flat filter, DF4
        plt.semilogx(haxis, filt_resp_mag_db[1][dfnum], linewidth=lw, color="orange",  zorder=1)
        plt.semilogx(haxis, filt_resp_mag_db[2][dfnum], linewidth=lw, color="green",  zorder=1)
        plt.semilogx(haxis, filt_resp_mag_db[3][dfnum], linewidth=lw, color="blue",  zorder=1)
        plt.semilogx(haxis, filt_resp_mag_db[4][dfnum], linewidth=lw, color="purple",  zorder=1)
        plt.semilogx(haxis, filt_resp_mag_db[5][dfnum], linewidth=lw, color="black", zorder=1)
    fignum += 1

# Spread-sinc filters, for section of video describing increasing DF x 2 corresponding
# to a 3dB improvement in SNR
filter_bw_plot = True
if filter_bw_plot == True:
    plt.figure(fignum)
    ftnum = 4 # SSinc
    lw = 1.5
    plt.axis([500, 100000, -120, 5])
    plt.semilogx(haxis, filt_resp_mag_db[ftnum][2], linewidth=lw, color="red", zorder=1)
    plt.semilogx(haxis, filt_resp_mag_db[ftnum][3], linewidth=lw, color="orange", zorder=1)
    plt.semilogx(haxis, filt_resp_mag_db[ftnum][4], linewidth=lw, color="green", zorder=1)
    plt.semilogx(haxis, filt_resp_mag_db[ftnum][5], linewidth=lw, color="blue", zorder=1)
    fignum += 1

print("My program took", (time.time() - start_time), " seconds to run")


'''
# Original code, reading files one at a time.

# Select downsample factor - DF4 to DF16384 (powers of 2)
# 4, 8, 16, 32 correspond to the LTC2512 (Flat passband filter type)
# 256, 1024, 4096, 16384 correspond to the LTC2508 (SSinc filter type)

DF_info = DF256

# List of filter type information
FT_list = [FTSINC1, FTSINC2, FTSINC3, FTSINC4, FTSSINC, FT_FLAT]

# UN-comment one to Select filter type.
#FT_info = Filt_Type_information.FTSINC1
#FT_info = Filt_Type_information.FTSINC2
#FT_info = Filt_Type_information.FTSINC3
#FT_info = Filt_Type_information.FTSINC4
FT_info = FTSSINC
#FT_info = Filt_Type_information.FT_FLAT

FS = 1000000 # Sample rate, for scaling horizontal axis

start_time = time.time();

# Sort of messy to read one by one, but each filter has a different length...

filename = "../../../common/ltc25xx_filters/" + FTSINC1.FT_txt + "_" + DF_info.DF_txt + ".txt"
filelength = lltf.linecount(filename)
filt_sinc1 = np.ndarray(filelength, dtype=float)
print(("reading " + str(filelength) + " coefficients from file " + filename))
# Read in coefficients from files
with open(filename, 'r') as infile:
    for i in range(0, filelength):
        instring = infile.readline()
        filt_sinc1[i] = float(instring)
print("done reading filter coefficients for " + FTSINC1.FT_txt + "!"))

filename = "../../../common/ltc25xx_filters/" + FTSINC2.FT_txt + "_" + DF_info.DF_txt + ".txt"
filelength = lltf.linecount(filename)
filt_sinc2 = np.ndarray(filelength, dtype=float)
print(("reading " + str(filelength) + " coefficients from file " + filename))
# Read in coefficients from files
with open(filename, 'r') as infile:
    for i in range(0, filelength):
        instring = infile.readline()
        filt_sinc2[i] = float(instring)
print("done reading filter coefficients for " + FTSINC2.FT_txt + "!"))

filename = "../../../common/ltc25xx_filters/" + FTSINC3.FT_txt + "_" + DF_info.DF_txt + ".txt"
filelength = lltf.linecount(filename)
filt_sinc3 = np.ndarray(filelength, dtype=float)
print(("reading " + str(filelength) + " coefficients from file " + filename))
# Read in coefficients from files
with open(filename, 'r') as infile:
    for i in range(0, filelength):
        instring = infile.readline()
        filt_sinc3[i] = float(instring)
print("done reading filter coefficients for " + FTSINC3.FT_txt + "!"))

filename = "../../../common/ltc25xx_filters/" + FTSINC4.FT_txt + "_" + DF_info.DF_txt + ".txt"
filelength = lltf.linecount(filename)
filt_sinc4 = np.ndarray(filelength, dtype=float)
print(("reading " + str(filelength) + " coefficients from file " + filename))
# Read in coefficients from files
with open(filename, 'r') as infile:
    for i in range(0, filelength):
        instring = infile.readline()
        filt_sinc4[i] = float(instring)
print("done reading filter coefficients for " + FTSINC4.FT_txt + "!"))

filename = "../../../common/ltc25xx_filters/" + FTSSINC.FT_txt + "_" + DF_info.DF_txt + ".txt"
filelength = lltf.linecount(filename)
filt_ssinc = np.ndarray(filelength, dtype=float)
print(("reading " + str(filelength) + " coefficients from file " + filename))
# Read in coefficients from files
with open(filename, 'r') as infile:
    for i in range(0, filelength):
        instring = infile.readline()
        filt_ssinc[i] = float(instring)
print("done reading filter coefficients for " + FTSSINC.FT_txt + "!"))

filename = "../../../common/ltc25xx_filters/" + FT_FLAT.FT_txt + "_" + DF_info.DF_txt + ".txt"
filelength = lltf.linecount(filename)
filt_flat = np.ndarray(filelength, dtype=float)
print(("reading " + str(filelength) + " coefficients from file " + filename))
# Read in coefficients from files
with open(filename, 'r') as infile:
    for i in range(0, filelength):
        instring = infile.readline()
        filt_flat[i] = float(instring)
print("done reading filter coefficients for " + FT_FLAT.FT_txt + "!"))




filt_sinc1 /= sum(filt_sinc1) #Normalize to unity gain
filt_sinc2 /= sum(filt_sinc2) #Normalize to unity gain
filt_sinc3 /= sum(filt_sinc3) #Normalize to unity gain
filt_sinc4 /= sum(filt_sinc4) #Normalize to unity gain
filt_ssinc /= sum(filt_ssinc) #Normalize to unity gain
filt_flat /= sum(filt_flat) #Normalize to unity gain
print("Done normalizing!"))

# Plot the impulse responses on the same horizontal axis, with normalized
# amplitude for a better visual picture...
plt.figure(1)
plt.title('impulse responses')
plt.plot(filt_sinc1 / max(filt_sinc1))
plt.plot(filt_sinc2 / max(filt_sinc2))
plt.plot(filt_sinc3 / max(filt_sinc3))
plt.plot(filt_sinc4 / max(filt_sinc4))
plt.plot(filt_ssinc / max(filt_ssinc))
plt.plot(filt_flat / max(filt_flat))
plt.xlabel('tap number')
plt.show()

filt_sinc1_resp_mag = lltf.freqz_by_fft_numpoints(filt_sinc1, 2 ** 20)
filt_sinc2_resp_mag = lltf.freqz_by_fft_numpoints(filt_sinc2, 2 ** 20)
filt_sinc3_resp_mag = lltf.freqz_by_fft_numpoints(filt_sinc3, 2 ** 20)
filt_sinc4_resp_mag = lltf.freqz_by_fft_numpoints(filt_sinc4, 2 ** 20)
filt_ssinc_resp_mag = lltf.freqz_by_fft_numpoints(filt_ssinc, 2 ** 20)
filt_flat_resp_mag = lltf.freqz_by_fft_numpoints(filt_flat, 2 ** 20)



# Calculate response in dB, for later use...
filt_sinc1_resp_mag_db = 20*np.log10(abs(filt_sinc1_resp_mag))
filt_sinc2_resp_mag_db = 20*np.log10(abs(filt_sinc2_resp_mag))
filt_sinc3_resp_mag_db = 20*np.log10(abs(filt_sinc3_resp_mag))
filt_sinc4_resp_mag_db = 20*np.log10(abs(filt_sinc4_resp_mag))
filt_ssinc_resp_mag_db = 20*np.log10(abs(filt_ssinc_resp_mag))
filt_flat_resp_mag_db = 20*np.log10(abs(filt_flat_resp_mag))

# Make vector of frequencies to plot / save against
haxis = np.linspace(0.0, FS, 2**20) # Horizontal axis

with open("LTC2500_filter_responses.csv", "w") as outfile:
    for i in range(0, 16400):
        outfile.write(str(haxis[i]) + "," + str(filt_sinc1_resp_mag_db[i]) + "," + str(filt_sinc2_resp_mag_db[i]) + ","  + str(filt_sinc3_resp_mag_db[i]) + ","
                                          + str(filt_sinc4_resp_mag_db[i]) + "," + str(filt_ssinc_resp_mag_db[i]) + "," + str(filt_flat_resp_mag_db[i])  + "\n")


# Plot frequency response, linear frequency axis
lw = 3
plt.figure(2)
plt.title("LTC2500-32 filter responses (DF " + DF_info.DF_txt + ")")
plt.xlabel('Frequency (Hz)')
plt.ylabel('Rejection (dB)')
plt.axis([0, 16400, -100, 10])
plt.plot(haxis, filt_sinc1_resp_mag_db, linewidth=lw, color="red", zorder=1)
plt.plot(haxis, filt_sinc2_resp_mag_db, linewidth=lw, color="orange",  zorder=1)
plt.plot(haxis, filt_sinc3_resp_mag_db, linewidth=lw, color="green",  zorder=1)
plt.plot(haxis, filt_sinc4_resp_mag_db, linewidth=lw, color="blue",  zorder=1)
plt.plot(haxis, filt_ssinc_resp_mag_db, linewidth=lw, color="purple",  zorder=1)
plt.plot(haxis, filt_flat_resp_mag_db, linewidth=lw, color="black", zorder=1)


print("My program took", (time.time() - start_time), " seconds to run")

'''