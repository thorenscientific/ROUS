
import math
import pandas as pd
from scipy.signal import periodogram,find_peaks,ricker, resample
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

import obspy
import obspy.signal

import numpy as np
import os
import sys
#print("Python Packages Import done")

import libm2k
#print("ADI Packages Import done")

def wav_init():

    ctx=libm2k.m2kOpen()
    if ctx is None:
        print("Connection Error: No ADALM2000 device available/connected to your PC.")
        sys.exit("m2k error")
    ctx.calibrateDAC()
    return(ctx)

#File directory of exported csv files
cwd = os.getcwd()
fpath = cwd + "\examples\cn0501\csv_files\\"



#Samples per second
N = 750000
t = np.arange(0,1,1/N)


#Ricker wavelet
vpp =  .5                        #pk-pk amplitude of wavelet
n_peak= 2                           #Number of wavelet peaks
n_points = int(N/n_peak)            #number of points per wavelet
width_param = int(n_points*.05)     #5% width parameter
vcm = 2.5                           #VCM of AD7768 (2.5V default)

x = ricker(n_points,width_param)    #generate wavelet

v_scale = vpp/(np.max(x)-np.min(x))/2 #scale to fit vpp
x = x*v_scale

rick_offset = 0 - np.min(x)
x = x + rick_offset

if n_peak > 1:
    ricker_wav = np.concatenate((x,x))
    for _ in range(1,n_peak-1):
        ricker_wav= np.concatenate((ricker_wav,x))
else:
    ricker_wav = x


def wavsingle_out(ctx):
    aout=ctx.getAnalogOut()
    aout.setSampleRate(0, N)
    aout.setSampleRate(1, N)
    aout.enableChannel(0, True)
    aout.enableChannel(1, True)
    w1_data = ricker_wav
    w2_data = ricker_wav

    buffer1 = w1_data
    buffer2 = w2_data
    buffer = [buffer1, buffer2]

    m2k_out = np.asarray(buffer1)
    m2k_out = m2k_out.reshape(N,1)

    DF = pd.DataFrame(m2k_out)

    f = "m2k_ricker_wav.csv"
    DF.to_csv(fpath+f, index = False, header = False)

    aout.setCyclic(True)
    aout.push(buffer)
    print("Wavelet Generated")

def wav_close(ctx):
    libm2k.contextClose(ctx)
    del ctx

def wavdiff_out(ctx):
    aout=ctx.getAnalogOut()
    aout.setSampleRate(0, N)
    aout.setSampleRate(1, N)
    aout.enableChannel(0, True)
    aout.enableChannel(1, True)
    w1_data = ricker_wav +vcm
    w2_data = vcm-ricker_wav

    plt.plot(w1_data)
    plt.plot(w2_data)
    plt.plot(w1_data-w2_data)
    #plt.show()

    buffer = [w1_data, w2_data]

    m2k_out1 = np.asarray(w1_data)
    m2k_out1 = m2k_out1.reshape(N,1)
    DF = pd.DataFrame(m2k_out1)

    m2k_out2 = np.asarray(w2_data)
    m2k_out2 = m2k_out2.reshape(N,1)
    DF = pd.DataFrame(m2k_out2)


#    f1 = "w1_ricker_wav_0v5pp.csv"
#    f2 = "w2_ricker_wav_0v5pp.csv"
#    DF.to_csv(fpath+f1, index = False, header = False)
#    DF.to_csv(fpath+f2, index = False, header = False)

    aout.setCyclic(True)
    aout.push(buffer)
    print("Wavelet Generated")

def seismic_out(ctx):

    st = obspy.read("https://examples.obspy.org/RJOB_061005_072159.ehz.new")
    data = st[0].data
    npts = st[0].stats.npts
    samprate = st[0].stats.sampling_rate
    shortdata = data[int(85*samprate):int(95*samprate)]
    m2kdata = resample(shortdata, int(len(shortdata)*7500//samprate))
    m2kdata /= 1.0 * np.max(np.abs(m2kdata)) # normalize to 1V

    aout=ctx.getAnalogOut()
    aout.setSampleRate(0, 7500)
    aout.setSampleRate(1, 7500)
    aout.enableChannel(0, True)
    aout.enableChannel(1, True)
    w1_data = m2kdata +vcm
    w2_data = vcm-m2kdata
    plt.figure(1)
    plt.title("Outgoing data")
    plt.plot(w1_data)
    plt.plot(w2_data)
    plt.plot(w1_data-w2_data)
    #plt.show()

    buffer = [w1_data, w2_data]

    aout.setCyclic(True)
    aout.push(buffer)
    print("Wavelet Generated")



available_sample_rates= [750, 7500, 75000, 750000, 7500000, 75000000]
max_rate = available_sample_rates[-1] # last sample rate = max rate
min_nr_of_points=10
max_buffer_size = 500000
uri = "ip:192.168.3.2"

def get_best_ratio(ratio):
    max_it=max_buffer_size/ratio
    best_ratio=ratio
    best_fract=1

    for i in range(1,int(max_it)):
        new_ratio = i*ratio
        (new_fract, integral) = math.modf(new_ratio)
        if new_fract < best_fract:
            best_fract = new_fract
            best_ratio = new_ratio
        if new_fract == 0:
            break

    return best_ratio,best_fract


def get_samples_count(rate, freq):
    ratio = rate/freq
    if ratio<min_nr_of_points and rate < max_rate:
        return 0
    if ratio<2:
        return 0

    ratio,fract = get_best_ratio(ratio)
    # ratio = number of periods in buffer
    # fract = what is left over - error

    size=int(ratio)
    while size & 0x03:
        size=size<<1
    while size < 1024:
        size=size<<1
    return size

def get_optimal_sample_rate(freq):
    for rate in available_sample_rates:
        buf_size = get_samples_count(rate,freq)
        if buf_size:
            return rate

def sine_buffer_generator(channel, freq, ampl, offset, phase):

    buffer = []

    sample_rate = get_optimal_sample_rate(freq)
    nr_of_samples = get_samples_count(sample_rate, freq)
    samples_per_period = sample_rate / freq
    phase_in_samples = ((phase/360) * samples_per_period)

    #print("sample_rate:",sample_rate)
    #print("number_of_samples",nr_of_samples)
    #print("samples_per_period",samples_per_period)
    #print("phase_in_samples",phase_in_samples)

    for i in range(nr_of_samples):
        buffer.append(offset + ampl * (math.sin(((i + phase_in_samples)/samples_per_period) * 2*math.pi) ))

    return sample_rate, buffer

def sine_1k_out(ctx):
#def main():
#    ctx=libm2k.m2kOpen(uri)
    ctx.calibrateADC()
    ctx.calibrateDAC()

    siggen=ctx.getAnalogOut()

    #call buffer generator, returns sample rate and buffer
    samp0,buffer0 = sine_buffer_generator(0,100,1,2.5,180)
    samp1,buffer1 = sine_buffer_generator(1,100,1,2.5,0)

    siggen.enableChannel(0, True)
    siggen.enableChannel(1, True)

    siggen.setSampleRate(0, samp0)
    siggen.setSampleRate(1, samp1)

    siggen.push([buffer0,buffer1])

#    input( " Press any key to stop generation ")