# ---------------------------------------------------------------------------
# Copyright (c) ?YEAR? Analog Devices, Inc. All rights reserved.
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

import math as m
def save_for_pscope(out_path, num_bits, is_bipolar, num_samples, dc_num, ltc_num, *data):
    num_channels = len(data)
    if num_channels < 0 or num_channels > 16:
        raise ValueError("pass in a list for each channel (between 1 and 16)")

    full_scale = 1 << num_bits
    if is_bipolar:
        min_val = -full_scale // 2
        max_val = full_scale // 2
    else:
        min_val = 0
        max_val = full_scale

    with open(out_path, 'w') as out_file:
        out_file.write('Version,115\n')
        out_file.write('Retainers,0,{0:d},{1:d},1024,0,{2:0.15f},1,1\n'.format(num_channels, num_samples, 0.0))
        out_file.write('Placement,44,0,1,-1,-1,-1,-1,10,10,1031,734\n')
        out_file.write('DemoID,' + dc_num + ',' + ltc_num + ',0\n')
        for i in range(num_channels):
            out_file.write(
                'RawData,{0:d},{1:d},{2:d},{3:d},{4:d},{5:0.15f},{3:e},{4:e}\n'.format(
                    i+1, int(num_samples), int(num_bits), min_val, max_val, 1.0 ))
        for samp in range(num_samples):
            out_file.write(str(data[0][samp]))
            for ch in range(1, num_channels):
                out_file.write(', ,' + str(data[ch][samp]))
            out_file.write('\n')
        out_file.write('End\n')

if __name__ == '__main__':
    num_bits = 16
    num_samples = 65536
    channel_1 = [int(8192 * m.cos(0.12 * d)) for d in range(num_samples)]
    channel_2 = [int(8192 * m.cos(0.034 * d)) for d in range(num_samples)]

    save_for_pscope('test.adc', num_bits, True, num_samples, 'DC9876A-A', 'LTC9999',
                    channel_1, channel_2 )

