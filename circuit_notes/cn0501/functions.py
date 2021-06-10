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
    Created by: Noe Quintero
    E-mail: nquintero@linear.com

    Description:
        The purpose of this module is consolidate usefull functions
"""
import llt.common.exceptions as err
import math
import time
import llt.utils.sin_params as sp

def make_vprint(verbose):
    if verbose:
        def vprint(string):
                print string
    else:
        def vprint(string):
                pass
    return vprint

def write_to_file_32_bit(filename, data, verbose = False, append = False):
    vprint = make_vprint(verbose)
    vprint('Writing data to file')
    with open(filename, 'a' if append else 'w') as f:
        for i in range(len(data)):
            f.write(str(data[i]) + '\n')
    vprint('File write done.')

def write_channels_to_file_32_bit(filename, *channels, **verbose_kw):
    vprint = make_vprint(verbose_kw.get("verbose", False))
    vprint('Writing data to file')
    if len(channels) < 1:
        vprint('Nothing to write')
        return
    write_to_file_32_bit(filename, channels[0])
    for channel in channels[1:]:
        write_to_file_32_bit(filename, channel, append=True)
    vprint('File write done.')

def plot(num_bits, data, channel = 0, verbose = False):
    vprint = make_vprint(verbose)
            
    from matplotlib import pyplot as plt
    import numpy as np
    from matplotlib.font_manager import FontProperties
    
    vprint("Plotting channel " + str(channel) + " time domain.") 
    
    num_samples = len(data)
    
    plt.figure(channel)
    plt.clf()
    plt.subplot(2,1,1)
    fig = plt.gcf()
    fig.subplots_adjust(right=0.68)
    plt.plot(data)
    plt.title('Ch' + str(channel) + ': Time Domain Samples')
    
    vprint("FFT'ing channel " + str(channel) + " data.") 

    adc_amplitude = 2.0**(num_bits-1)
    
    data_no_dc = data - np.average(data) # Remove DC to avoid leakage when windowing

    normalization = 1.968888        
    a0 = 0.35875
    a1 = 0.48829
    a2 = 0.14128
    a3 = 0.01168
    
    wind = [0 for x in range(num_samples)]
    for i in range(num_samples):
        
        t1 = i / (float(num_samples) - 1.0)
        t2 = 2 * t1
        t3 = 3 * t1
        t1 -= int(t1)
        t2 -= int(t2)
        t3 -= int(t3)
        
        wind[i] = a0 - \
                  a1*math.cos(2*math.pi*t1) + \
                  a2*math.cos(2*math.pi*t2) - \
                  a3*math.cos(2*math.pi*t3)
        
        wind[i] *= normalization;


    windowed_data = data_no_dc * wind# Apply Blackman window
    freq_domain = np.fft.fft(windowed_data)/(num_samples) # FFT
    freq_domain = freq_domain[0:num_samples/2+1]
    freq_domain_magnitude = np.abs(freq_domain) # Extract magnitude
    freq_domain_magnitude[1:num_samples/2] *= 2 
    freq_domain_magnitude_db = 20 * np.log10(freq_domain_magnitude/adc_amplitude)
    
    vprint("Plotting channel " + str(channel) + " frequency domain.")     
    
    ax = plt.subplot(2, 1, 2)
    
    ax.set_title('Ch' + str(channel) + ': FFT')
    plt.plot(freq_domain_magnitude_db)
    
    try:
        harmonics, snr, thd, sinad, enob, sfdr, floor = sp.sin_params(data)
        
        sig_amp = math.sqrt(abs(harmonics[1][0]))
        fund_dbsf = 20 * math.log10(sig_amp/2**(num_bits-1))
        f2 = 20 * math.log10((math.sqrt(abs(harmonics[2][0])))/2**(num_bits-1))
        f3 = 20 * math.log10((math.sqrt(abs(harmonics[3][0])))/2**(num_bits-1))
        f4 = 20 * math.log10((math.sqrt(abs(harmonics[4][0])))/2**(num_bits-1))
        f5 = 20 * math.log10((math.sqrt(abs(harmonics[5][0])))/2**(num_bits-1))
        
        # The floor is given in dBc. We add the fundimantal to convert to dBFs        
        floor += fund_dbsf
        plt.plot([floor for number in xrange(num_samples/2-1)], 'y')
        
        max_code = max(data)
        min_code = min(data)
        avg = np.mean(data)

        font = FontProperties()
        font.set_family('monospace')
        fig.text(0.72,0.40, "F1 BIN:    " + str(harmonics[1][1]) + "\nF1 Amp:   " + "{0:.1f}".format(round(fund_dbsf,1)) + 
            " dBFS\nF2 Amp:   " + "{0:.1f}".format(round(f2,1)) +
            " dBFS\nF3 Amp:   " + "{0:.1f}".format(round(f3,1)) +
            " dBFS\nF4 Amp:   " + "{0:.1f}".format(round(f4,1)) +
            " dBFS\nF5 Amp:   " + "{0:.1f}".format(round(f5,1)) +
            " dBFS\n\nSNR:      " + "{0:.1f}".format(round(snr,1)) + " dB\nSINAD:    " + 
            "{0:.1f}".format(round(sinad,1)) + " dB\nTHD:      " + 
            "{0:.1f}".format(round(thd,1)) + " dB\nSFDR:     " +
            "{0:.1f}".format(round(sfdr,1))  + " dB\nENOB:     " + 
            "{0:.1f}".format(round(enob,1)) + " bits\nMax:      " + str(max_code) +
            "\nMin:      " + str(min_code) + "\nDC Level: " + 
            "{0:.1f}".format(round(avg,1)) + "\nFloor:    " +
            "{0:.1f}".format(round(floor,1)) + " dBFS", fontproperties=font)

        ax.annotate('1',
            xy=(harmonics[1][1], fund_dbsf), xycoords='data',
            xytext=(0, -10), textcoords='offset points',
            horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
        
        ax.annotate('2',
            xy=(harmonics[2][1], f2), xycoords='data',
            xytext=(0, 0), textcoords='offset points',
            horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
        ax.annotate('3',
            xy=(harmonics[3][1], f3), xycoords='data',
            xytext=(0, 0), textcoords='offset points',
            horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
        ax.annotate('4',
            xy=(harmonics[4][1], f4), xycoords='data',
            xytext=(0, 0), textcoords='offset points',
            horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
        ax.annotate('5',
            xy=(harmonics[5][1], f5), xycoords='data',
            xytext=(0, 0), textcoords='offset points',
            horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
    except:
        fig.text(0.75,0.8, "No AC Signal\nDetected")
    plt.show()

def plot_channels(num_bits, *channels, **verbose_kw):
    verbose = verbose_kw.get("verbose", False)
    for channel_num, channel_data in enumerate(channels):
        plot(num_bits, channel_data, channel_num, verbose)
    
def fix_data(data, num_bits, alignment, is_bipolar, is_randomized = False, is_alternate_bit = False):
    if alignment < num_bits:
        raise err.LogicError("Alignment must be >= num_bits ")
    if  alignment > 30:
        raise err.NotSupportedError("Does not support alignment greater than 30 bits")
    shift = alignment - num_bits
    sign_bit = (1 << (num_bits - 1))
    offset = 1 << num_bits
    mask = offset - 1
    
    for i in xrange(len(data)):
        x = data[i]
        x = x >> shift
        if is_randomized and  (x & 1):
            x = x ^ 0x3FFFFFFE;
        if is_alternate_bit:
            x = x ^ 0x2AAAAAAA;
        x = x & mask
        if  is_bipolar and (x & sign_bit):
            x = x - offset
        data[i] = x 
    return data

def scatter_data(data, num_channels):
    if num_channels == 1:
        return data
    temp = []
    for x in range(0,num_channels):
        temp.append(data[x::num_channels])
    return tuple(temp)

def get_controller_info_by_eeprom(controller_type, dc_number, eeprom_id_size, vprint):
    import llt.common.ltc_controller_comm as comm
    # find demo board with correct ID
    vprint('Looking for a controller board')
    info_list = comm.list_controllers(controller_type)
    if info_list is None:
        raise(err.HardwareError('No controller boards found'))
    for info in comm.list_controllers(controller_type):
        with comm.Controller(info) as controller:
            eeprom_id = controller.eeprom_read_string(eeprom_id_size)
            if dc_number in eeprom_id:
                vprint('Found the ' + dc_number + ' demoboard')
                return info
    raise(err.HardwareError('Could not find a compatible device'))

def start_collect(controller_board, num_samples, trigger, timeout = 5):
        controller_board.controller.data_start_collect(num_samples, trigger)
        SLEEP_TIME = 0.2 
        for i in range(int(math.ceil(timeout/SLEEP_TIME))):
            if controller_board.controller.data_is_collect_done():
                return
            time.sleep(SLEEP_TIME)
        raise err.HardwareError('Data collect timed out (missing clock?)')

def uint32_to_int32(data): 
    return [(int(d - 4294967296 if d > 2147483647 else d)) for d in data] 