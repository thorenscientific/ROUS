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
Created on Wed Feb 03 10:10:18 2016

@author: mark_t
"""

def endpoint_inl(data):
    import numpy as np
    length = len(data)
    inldata = np.ndarray(length, dtype=float)
    xmax = len(data) -1
#    data -= np.average(data)
    slope = (data[xmax] - data[0]) / (xmax - 0.0)# Rise over run
    intercept = data[xmax] - (slope * xmax)

    for i in range(0, len(data)):
        inldata[i] = (data[i] - (slope * i) - intercept)
    return inldata
    
if __name__ == "__main__": 

    import numpy as np
    from matplotlib import pyplot as plt

    # Keep track of start time
#    start_time = time.time()

    curve = np.ndarray(200, dtype=float)
    
    a = np.random.uniform(-2, 2)
    b = np.random.uniform(-100, 100)
    c = np.random.uniform(-50, 50)    
    
    for point in range(-100, 100):
        floatpoint = float(point) / 10.0

        curve[point + 100] = (a*floatpoint**2.0) + b*floatpoint -c
        np.random.uniform(-5, 5)
    inlcurve = endpoint_inl(curve)
        
    plt.figure(1)
    plt.plot(curve)
    plt.plot(inlcurve)
    plt.show()
        
        