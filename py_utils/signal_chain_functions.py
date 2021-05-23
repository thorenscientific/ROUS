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
# 2021-05-22
# -----------------------------------------------------------------------

# First, import goodies from standard libraries
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal


# A function to fold up a noise spectrum, showing the effects of aliasing.
# Returns individual folded Nyquist zones, as well as the RMS sums of the folded zones.
def fold_spectrum(unfolded_spectrum, points_per_zone, num_zones):
    verbose = 0
    zonesign = 1
    folded_spectrum = [[0 for i in range(num_zones)] for j in range(points_per_zone)] #initialize array
    # This section slices up the unfolded spectrum, flipping for even Nyquist zones.
    for i in range(0, num_zones):
        if(zonesign == 1):
            folded_spectrum[i] = unfolded_spectrum[points_per_zone*(i):points_per_zone*(i+1) -1:1]
            zonesign = -1
            if(verbose == 1):
                print(str(i) + " " +str(points_per_zone*(i)) + " " + str(points_per_zone*(i+1)-1))
        else:
            folded_spectrum[i] = unfolded_spectrum[points_per_zone*(i+1)-1 : points_per_zone*(i) : -1]
            zonesign = 1
            if(verbose == 1):
                print(str(i) + " " +str(points_per_zone*(i+1)-1) + " " + str(points_per_zone*(i)))
    # Now RMS sum corresponding points from each zone
    rms_sum = [0 for i in range(points_per_zone)]
    for i in range(0, num_zones): # First, square noise densities of each zone, then add
        for j in range(0, points_per_zone-1):
            rms_sum[j] += folded_spectrum[i][j] ** 2

    for j in range(0, points_per_zone): # Then take the square root of each element
        rms_sum[j] = rms_sum[j] ** 0.5
    return folded_spectrum, rms_sum


# Function to integrate a power-spectral-density
# The last element represents the total integrated noise
def integrate_psd(psd, bw):
    integral_of_psd_squared = np.zeros(len(psd))
    integrated_psd = np.zeros(len(psd))
    integral_of_psd_squared[0] = psd[0]**2.0

    for i in range(1, len(psd)):
        integral_of_psd_squared[i] += integral_of_psd_squared[i-1] + psd[i-1] ** 2
        integrated_psd[i] += integral_of_psd_squared[i]**0.5
    integrated_psd *= bw**0.5
    return integrated_psd

# Equivalent noise bandwidth of an arbitrary filter, given
# frequency response magnitude and bandwidth per point
def arb_enbw(fresp, bw):
    integral_of_fresp_sqared = np.zeros(len(fresp))
    integral_of_fresp_sqared[0] = fresp[0]**2.0
    for i in range(1, len(fresp)):
        integral_of_fresp_sqared[i] += integral_of_fresp_sqared[i-1] + fresp[i-1] ** 2
    return integral_of_fresp_sqared[len(integral_of_fresp_sqared)-1]*bw

# Equivalent noise bandwidth of a FIR filter from filter taps
# Bandwidth implied by sample rate
def fir_enbw(taps):
    return len(taps) * np.sum(taps**2) / np.sum(taps)**2

# Magnitude spectrum of an FIR, points per coefficient
def freqz_by_fft(filter_coeffs, points_per_coeff):
    num_coeffs = len(filter_coeffs)
    fftlength = num_coeffs * points_per_coeff
    resp = abs(np.fft.fft(np.concatenate((filter_coeffs, np.zeros(fftlength - num_coeffs))))) # filter and a bunch more zeros
    return resp

# Magnitude spectrum of an FIR, in terms of total number of points (more similar to freqz)
def freqz_by_fft_numpoints(filter_coeffs, numpoints):
    num_coeffs = len(filter_coeffs)
    if numpoints < num_coeffs:
        print("freqz_by_fft_numpoints: numpoints must be greater than # filter coefficients")
        return []
    fftlength = numpoints
    resp = abs(np.fft.fft(np.concatenate((filter_coeffs, np.zeros(fftlength - num_coeffs))))) # filter and a bunch more zeros
    return resp

# Upsample an array and stuff zeros between data points.
# Upsample_factor is the total number of output points per
# input point (that is, the number of zeros stuffed is
# upsample_factor-1)
def upsample_zero_stuff(data, upsample_factor):
    # Starting with zeros makes things easy :)
    upsample_data = np.zeros(upsample_factor * len(data))
    for i in range (0, len(data)):
        upsample_data[upsample_factor*i] = data[i]
    return upsample_data

def downsample(data, downsample_factor):
    # Starting with zeros makes things easy :)
    downsample_data = np.zeros(len(data) / downsample_factor)
    for i in range (0, len(downsample_data)):
        downsample_data[i] = data[i * downsample_factor]
    return downsample_data

#freq=(np.random.normal(loc=0.0, scale=1, size=8))

# Generate time series from half-spectrum. DC in first element.
# Output length is 2x input length
def time_points_from_freq(freq): #DC at element zero,
    N=len(freq)
    randomphase_pos = np.ones(N-1, dtype=np.complex)*np.exp(1j*np.random.uniform(0.0, 2.0*np.pi, N-1))
    randomphase_neg = np.flip(np.conjugate(randomphase_pos))
    randomphase_full = np.concatenate(([1],randomphase_pos,[1], randomphase_neg))
    print("randomphase full  type and size: ", type(randomphase_full), len(randomphase_full))
    r_spectrum_full = np.concatenate((freq, np.roll(np.flip(freq), 1)))
    r_spectrum_randomphase = r_spectrum_full * randomphase_full
    r_time_full = np.fft.ifft(r_spectrum_randomphase)
    print("RMS imaginary component: ", np.std(np.imag(r_time_full)), " Should be close to nothing")
    return(np.real(r_time_full))

def linecount(fname): # A handy functon to count lines in a file.
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1






if ((__name__ == "__main__") and (False)):
    fignum = 1
    print("First, let's validate the integrate_psd function...")
    numpoints = 65536
    cutoff = 1024.0
    bw_per_point = 1/cutoff
    fmax = numpoints * bw_per_point
    first_order_response = np.ndarray(numpoints, dtype = float)
    for i in range(numpoints):
        first_order_response[i] = 1.0 / (1.0 + (i/cutoff)**2.0)**0.5 # Magnitude = 1/SQRT(1 + (f/fc)^2)
    psd = integrate_psd(first_order_response, 1.0/cutoff)

    print("Test parameters:")
    print("Cutoff frequency: " + str(cutoff) + "Hz")
    print("Integrate DC to : " + str(numpoints) + "Hz")
    print("Predicted total noise is sqrt(pi/2): " + str((np.pi/2) ** 0.5))
    print("And it actually is: " + str(psd[numpoints-1]))

    f = np.arange(2, 65538, 1)

    plt.figure(fignum)
    fignum += 1
    plt.subplot(2, 1, 1)
    plt.title("First order LPF response, fc=" + str(cutoff))
    plt.semilogx(f, 20*np.log(first_order_response))
    plt.subplot(2, 1, 2)
    plt.title("Total integ. noise from DC to x, should be sqrt(pi/2)")
    plt.semilogx(f, psd)
    plt.show()

    sinc1resp = abs(np.fft.fft(np.concatenate(((np.ones(1024)/1024.0), np.zeros(65536-1024))))) # Make a 1024 tap filter, then find freq response
    psdsinc = integrate_psd(sinc1resp, 1.0/64.0)

    plt.figure(fignum)
    fignum += 1
    plt.subplot(2, 1, 1)
    plt.title("SINC1 filter response, N=" + str(1024))
    plt.plot(sinc1resp)
    plt.axis([0, 500, 0, max(sinc1resp)])
    plt.subplot(2, 1, 2)
    plt.title("Total integ. noise from DC to x, should be sqrt(0.5)")
    plt.plot(psdsinc)
    plt.axis([0, 500, 0, max(psdsinc)])
    plt.show()

    print("And finally, here's your LTSpice noise simulation directive:")
    print(".noise V(Vout) Vin_source lin " + str(numpoints-1) + " " + str(bw_per_point) + " " + str(fmax))
# Arguments are output node, input node, linear spacing, # of points, bin 1 frequency, end frequency)
# In LTspice, plot Vout noise spectrum. Then, right click in plot:
#  File -> Export data as txt -> select V(onoise)

    ltspice_psd = np.zeros(numpoints) # bin zero(DC) already set to zero ;)
    print('reading noise PSD data from file')
    infile = open('../LTSpice/validate_integrate_psd.txt', 'r')
    print("First line (header): " + infile.readline())
    for i in range(1, numpoints-1):
        instring = infile.readline()
        indata = instring.split()         # Each line has two entries separated by a space
        ltspice_psd[i] = float(indata[1]) # Frequency Density
    infile.close()
    print('done reading!')

    ltspice_totalnoise = integrate_psd(ltspice_psd, bw_per_point)
    print("total noise of LTSpice sim: " + str(ltspice_totalnoise[numpoints-1]))
    print("(Control-click in output plot in LTSpice and compare.)")

# Periodogram reality check, from
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.periodogram.html
    #np.random.seed(1234)
    #Generate a test signal, a 1 Vrms sine wave at a particular bin #
    # Corrupted by either a specified flat noise power
    # OR an RMS ADC noise (23uVRMS for LTC2500 family) which should be 32nV/rootHz at 1Msps

    navg = 64 # Average a number of records to flatten out the noise floor
    for i in range(navg):
        ltc2500_noise = np.random.normal(loc = 0.0, scale = 23e-6, size = int(N)) #23uVRMS
        noise_power = 0.001 * fs / 2
        time = np.arange(N) / fs
        x = amp*np.sin(2*np.pi*freq*time)
        #x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
        x += ltc2500_noise
        #Compute and plot the power spectral density.
        if(i==0):
            f, Pxx_den_avg = signal.periodogram(x, fs)
        else:
            f, Pxx_den = signal.periodogram(x, fs)
            Pxx_den_avg += Pxx_den
    Pxx_den_avg /= navg

    plt.figure(fignum)
    fignum += 1
    plt.semilogy(f, np.sqrt(Pxx_den_avg))
    plt.ylim([1e-10, 1e1])
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()

    print("Double-checking that integrate_psd works...")
    myfilt = np.ones(128)/128.0
    sr = 128 # 100Hz notch
    f, fresp = signal.freqz(myfilt, a=1, worN=16384, whole=False, fs=sr)
    fresp_mag = np.abs(fresp)
    totalnoise=integrate_psd(fresp_mag, f[1]) # first element of frequency array is bw per point

    plt.figure(fignum)
    fignum += 1
    plt.title("SINC1 filter and integrated noise")
    plt.plot(f, fresp_mag)
    plt.plot(f, totalnoise)
    plt.ylim([1e-10, 2])
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()





    r = 1000
    #r_en = np.sqrt(4*1.38e-23*300*r)
    r_en = 32.5e-9
    fs = 1000000
    r_ampl = r_en*np.sqrt(fs/2.0)

    N = 2**18
    amp = 1.0 *np.sqrt(2)
    freq = 1024.0 * fs / N







    # Select downsample factor. This can be any power of 2 from 4 to 16384
    downsample = 64
    # Select variable decimation filter decimation factor. This can be any number
    # between 1 and 16384. Note that
    var_decimation = 1234

    # Generate SINC filters. SINC filter coefficients are very easy to generate, so
    # we'll just derive them directly.
    sinc1 = np.ones(downsample)
    sinc2 = np.convolve(sinc1, sinc1)
    sinc3 = np.convolve(sinc2, sinc1)
    sinc4 = np.convolve(sinc3, sinc1)
    varsinc = np.ones(var_decimation)

    # An attempt at a spread-sinc filter
    ssinc = np.convolve(sinc1, np.ones(int(downsample * .625)))
    ssinc = np.convolve(ssinc, np.ones(int(downsample * .75)))
    #ssinc = np.convolve(ssinc, np.ones(int(downsample * .875)))
    ssinc = np.convolve(ssinc, np.ones(int(downsample * .9375)))

    # We'll normalize the filters here, since this is what the LTC2500 will send
    # out
    sinc1 = sinc1 / sum(sinc1)
    sinc2 = sinc2 / sum(sinc2)
    sinc3 = sinc3 / sum(sinc3)
    sinc4 = sinc4 / sum(sinc4)
    ssinc = ssinc / sum(ssinc)
    varsinc = varsinc / sum(varsinc)

    plt.figure(fignum)
    fignum += 1
    plt.subplot(3, 1, 1)
    plt.plot(sinc1)
    plt.ylabel('Amplitude')
    plt.title('sinc filter time domain responses')
    plt.subplot(3, 1, 2)
    plt.plot(sinc4)
    plt.ylabel('Amplitude')
    plt.subplot(3, 1, 3)
    plt.plot(ssinc)
    plt.ylabel('Amplitude')
    #plt.plot(reverser * amax(sinc4))
    plt.xlabel('tap number')

    #plt.hlines(1, min(sinc4), max(sinc4), colors='r')
    #plt.hlines(0, min(sinc4), max(sinc4))
    #plt.xlim(xmin=-100, xmax=2*downsample)
    #plt.legend(('Unit-Step Response',), loc=0)
    plt.grid()
    plt.show()

    w1, h1 = signal.freqz(sinc1, 1, 16385)
    w2, h2 = signal.freqz(sinc2, 1, 16385)
    w3, h3 = signal.freqz(sinc3, 1, 16385)
    w4, h4 = signal.freqz(sinc4, 1, 16385)
    ws, hs = signal.freqz(ssinc, 1, 16385)

    fresp1 = 20*np.log10(abs(h1))
    fresp2 = 20*np.log10(abs(h2))
    fresp3 = 20*np.log10(abs(h3))
    fresp4 = 20*np.log10(abs(h4))
    fresps = 20*np.log10(abs(hs))


    plt.figure(fignum)
    fignum += 1
    plt.plot(fresp1, zorder=1)
    #plt.plot(fresp2, zorder=1)
    #plt.plot(fresp3, zorder=1)
    plt.plot(fresp4, zorder=1)
    plt.plot(fresps, zorder=1)


    plt.title('sinc4 frequency domain response')
    plt.xlabel('freq.')
    plt.ylabel('log Amplitude')
    plt.axis([0, 16400, -150, 0])
    plt.show()



    #Okay, now let's play around with some filtering, and try to show the
    #equivalence of averaging (A SINC1 filter) to bin 1 of an FFT!

    num_points = 1024
    value = 100
    rms_noise = 25

    data = np.ndarray(shape=num_points, dtype=float)
    avg = 0.0
    for i in range(num_points):
        data[i] = np.random.normal(value, rms_noise)
        avg += data[i]

    avg = avg / num_points
    print("Average, calculated using standard method: " + str(avg))
    fftdata = np.fft.fft(data)
    print("Average, taken as bin 1 of FFT: " + str(fftdata[0] / num_points))


    # Now on to modeling the noise of the LTC2500 itself, the noise of a
    # resistive sensor, and the noise of an LTC2057

    print("Now let's model the noise of the LTC2500 and a resistive source")
    resistance = 1000
    temperature = 300
    resistor_noise = np.sqrt(4*1.3806488e-23*temperature*resistance)
    fftlength = 8192
    samplerate = 1024000
    bin_width = samplerate / (2*fftlength)
    # Add these calculations (copied from another script...):
    #adc_snr = -90.2 # Enter datasheet SNR
    #adc_range = 10.0 # Enter peak-to-peak range
    # Calculate total ADC noise (volts RMS)
    #adc_noise = (10 ** (adc_snr / 20)) * adc_range / (2*2**0.5)

    #ADR RMS noise formula: 10^(SNR / 20) * peak-to-peak input range /(2*SQRT2) = RMS Noise


    #From the datasheet: 10^(-104dB SNR / 20) * 10V/(2*SQRT2) = 22.3uVRMS
    adc_noise = 22.3e-6
    print("ADC total noise: " + str(adc_noise))
    print("bin Width: " + str(bin_width))
    theo_noise = (adc_noise / np.sqrt(samplerate/2))
    print("Theoretical ADC noise density: " + str(theo_noise))


    smoothed_adc_psd = np.zeros(fftlength)
    averages = 128
    for i in range(0, averages):
        # Generate some ADC samples with Gaussian noise. Average a bunch of runs to
        # see where the real noise floor is.
        adc_samples = np.random.normal(loc=0, scale=adc_noise, size=fftlength)
        adc_samples_fft = abs(np.fft.fft(adc_samples))/fftlength
        # Calculate the psd and scale properly - divide FFT by FFT length,
        # Then divied by the bin width to get density directly.
        #### DOUBLE CHECK THIS - the double-sided spectrum amplitude looks a bit low...
    #    adc_psd = np.sqrt(adc_samples_fft*adc_samples_fft/bin_width)
        adc_psd = adc_samples_fft/np.sqrt(bin_width)

        smoothed_adc_psd += (adc_psd / averages)

    #smoothed_adc_psd = np.convolve(np.ones(64), adc_psd)/64

    measured_adc_psd = np.average(smoothed_adc_psd)
    print("Measured ADC PSD: " + str(measured_adc_psd))
    print ("error %" + str(measured_adc_psd/theo_noise))

    # Here we're going to do the opposite of what we did with the ADC, that is,
    # We're going to model a resistor's noise in the frequency domain and see what it
    # looks like in the time domain. There's a couple of subtleties, so
    # pay attention!
    resistor_psd = np.ones(fftlength)*resistor_noise # Vector representing noise density
    resistor_complex_psd = np.ndarray(fftlength, dtype=complex) # Initialize an array to fill up
    for i in range(int(fftlength/2)): #Setting two bins for each iteration, working inward from DC, FS
        phase = np.random.uniform(0, 2*np.pi) # Generate a random number from 0 to 2*pi
        real = np.cos(phase) # Find real component of noise vector
        imag = np.sin(phase) # Find imaginary component of noise vector
        resistor_complex_psd[i+1] = ((real) + 1j*imag )*resistor_psd[i+1] # Note that we start at bin 1, not zero!
        resistor_complex_psd[(fftlength-1) - i] = ((real) - 1j*imag)*resistor_psd[(fftlength-1) - i] # Conjugate!
    resistor_complex_psd[0] = 0.0 #Take care of DC
    resistor_complex_psd[int(fftlength/2)] = resistor_noise #Take care of one bin past Nyquist

    # Now find time domain voltage. Check for yourself - is there any imaginary component?
    resistor_time_noise = np.fft.ifft(resistor_complex_psd)*fftlength

    '''
    ltc2057_psd = np.zeros(int(fftlength/2)) # bin zero(DC) already set to zero ;)
    print('reading noise PSD data from file')
    infile = open('ltspice_psd.txt', 'r')
    print("First line (header): " + infile.readline())
    for i in range(1, fftlength/2):
        instring = infile.readline()
        indata = instring.split()         # Each line has two entries separated by a space
        ltc2057_psd[i] = float(indata[1]) # Frequency Density
    infile.close()
    print('done reading!')


    plt.figure(fignum)
    fignum += 1
    plt.title("ADC, LTC2057, 350 ohm resistor noise")
    plt.xlabel('FFT bin number')
    plt.ylabel('noise density (V/rootHz)')
    plt.plot(smoothed_adc_psd)
    plt.plot(np.abs(resistor_complex_psd))
    plt.plot(np.concatenate((ltc2057_psd, ltc2057_psd[::-1])))
    plt.show()
    '''

    t = np.arange(fftlength) # Vector for the X axis

    plt.figure(fignum)
    fignum += 1
    plt.title("350 ohm resistor time noise calculated from\n frequency domain density")
    plt.xlabel('time (samples)')
    plt.ylabel('Voltage (V)')
    #plt.plot(t, resistor_complex_psd.real, 'b-', t, resistor_complex_psd.imag, 'r--')
    plt.plot(t, resistor_time_noise.real, 'b-', t, resistor_time_noise.imag, 'r--')
    plt.show()

    # Above, we found the filter response using the freqz function. You can achieve
    # the same thing by taking an fft of the filter taps, padded out to the length
    # of the fft that you will be multiplying the response by.
    sinc4resp = abs(np.fft.fft(np.concatenate((sinc4,np.zeros(fftlength-int(sinc4.size))))))
    sinc4resp_dB = 20*np.log10(sinc4resp)
    # now plot...
    plt.figure(fignum)
    fignum += 1
    plt.title("SINC4 filter response from zero-padded coefficients")
    plt.plot(sinc4resp_dB)
    plt.show()

    '''
    wide_ltc2057_psd = np.zeros(fftlength*2) # bin zero(DC) already set to zero ;)
    print('reading wide (2MHz) noise PSD data from file')
    infile = open('LTC2057_noisesim_2Meg.txt', 'r')
    print("First line (header): " + infile.readline())
    for i in range(1, fftlength*2):
        instring = infile.readline()
        indata = instring.split()         # Each line has two entries separated by a space
        wide_ltc2057_psd[i] = float(indata[1]) # Frequency Density
    infile.close()
    print('done reading!')

    #Okay now let's fold zones.
    num_zones = 4
    points_per_zone = 4096

    zones_ltc2057_psd, ltc2057_folded = fold_spectrum(wide_ltc2057_psd, points_per_zone, num_zones )


    plt.figure(fignum)
    fignum += 1
    plt.title("2.048MHz worth of LTC2057 noise,\nFolded into 4 Nyquist zones")
    ax = plt.gca()
    ax.set_axis_bgcolor('#C0C0C0')
    lines = plt.plot(zones_ltc2057_psd[0])
    plt.setp(lines, color='#FF0000', ls='-') #Red
    lines = plt.plot(zones_ltc2057_psd[1])
    plt.setp(lines, color='#FF7F00', ls='--') #Orange
    lines = plt.plot(zones_ltc2057_psd[2])
    plt.setp(lines, color='#FFFF00', ls='-') #Yellow
    lines = plt.plot(zones_ltc2057_psd[3])
    plt.setp(lines, color='#00FF00', ls='-') #Green
    lines = plt.plot(ltc2057_folded)
    plt.setp(lines, color='k', ls='-') #Black
    plt.show()

    ltc1563_response = np.zeros(16384)
    print('reading LTC1563 frequency response to 2M')
    infile = open('1563-3_aa_filter_sim.txt', 'r')
    print("First line (header): " + infile.readline())
    for i in range(1, 16384):
        instring = infile.readline()
        indata = instring.split()         # Each line has two entries separated by a space
        magphase = indata[1]            #EXTREME KLUGE until we use regex properly
        field1 = magphase.split("(")
        field2 = field1[1].split("dB")
        magnitude = field2[0]
        #print magnitude
        ltc1563_response[i] = 10.0 ** (float(magnitude)/20) # Convert from dB to fraction
    infile.close()
    print('done reading!')



    # Fold up LTC1563 response
    zones_ltc1563_resp, ltc1563_folded = fold_spectrum(ltc1563_response, 4096, 4)
    # Now multiply zones by filter response!!
    total_resp0 = list(zones_ltc1563_resp[0])
    total_resp1 = list(zones_ltc1563_resp[1])
    total_resp2 = list(zones_ltc1563_resp[2])
    total_resp3 = list(zones_ltc1563_resp[3])

    # Multipy analog filter response with the digital filter response, zone by zone
    for i in range(0, (fftlength/2)-1):
        total_resp0[i] = total_resp0[i] * sinc4resp[i]
        total_resp1[i] = total_resp1[i] * sinc4resp[i]
        total_resp2[i] = total_resp2[i] * sinc4resp[i]
        total_resp3[i] = total_resp3[i] * sinc4resp[i]

    # Plot LTC1563 folded response
    plt.figure(fignum)
    fignum += 1
    plt.title("LTC1563 response to 2.048MHz, folded \nand multiplied by SINC4")
    ax = plt.gca()
    ax.set_axis_bgcolor('#C0C0C0')
    lines = plt.plot(20*np.log10(zones_ltc1563_resp[0]))
    plt.setp(lines, color='#FF0000', ls='-') #Red
    lines = plt.plot(20*np.log10(zones_ltc1563_resp[1]))
    plt.setp(lines, color='#FF7F00', ls='--') #Orange
    lines = plt.plot(20*np.log10(zones_ltc1563_resp[2]))
    plt.setp(lines, color='#FFFF00', ls='-') #Yellow
    lines = plt.plot(20*np.log10(zones_ltc1563_resp[3]))
    plt.setp(lines, color='#00FF00', ls='-') #Green
    lines = plt.plot(20*np.log10(ltc1563_folded))
    plt.setp(lines, color='k', ls='-') #Black
     # Plot total response of LTC1563 and digital filter on the same graph.
    lines = plt.plot(20*np.log10(total_resp0))
    plt.setp(lines, color='#FF0000', ls='-') #Red
    lines = plt.plot(20*np.log10(total_resp1))
    plt.setp(lines, color='#FF7F00', ls='--') #Orange
    lines = plt.plot(20*np.log10(total_resp2))
    plt.setp(lines, color='#FFFF00', ls='-') #Yellow
    lines = plt.plot(20*np.log10(total_resp3))
    plt.setp(lines, color='#00FF00', ls='-') #Green
    plt.show()

    #

    ltc2057_total_noise = np.zeros(fftlength*2)
    for i in range(1, fftlength*2):
        ltc2057_total_noise[i] = ltc2057_total_noise[i-1] + wide_ltc2057_psd[i]
    ltc2057_total_noise = ltc2057_total_noise / ((bin_width / 2) ** 0.5)

    plt.figure(fignum)
    fignum += 1
    plt.title("Integrated LTC2057 noise")
    plt.plot(ltc2057_total_noise)
    plt.show()

    '''


    # Set up parameters
    samplerate = 1024000 # Samples per second

    # Make this a multiple of 2. That is, analyze at
    # least out to samplerate, which will alias to DC.
    nyquist_zones_to_consider = 4

    # Select downsample factor. This can be any power of 2 from 4 to 16384
    n_factor = 16

    # This parameter takes some explanation. When calculating the frequency response of
    # the filter, we need more than just n_factor points, because all of the n_factor
    # points reside in zeros and you wouldn't have an accurate picture of the response.
    freq_response_factor = 512

    # Calculate FFT length to use. This is the number of points to analyze for each
    # double-nyquist zone.
    fftlength = n_factor * freq_response_factor

    bin_width = samplerate / (2 * fftlength)

    # Next, we'll Generate SINC1 filter coefficients, wich is just a bunch of ones.
    # Note that the LTC2380-24 will scale the output automatically for exact
    # power-of-2 n_factors, refer to datasheet for scaling of other factors.
    sinc1 = np.ones(n_factor)
    # Normalize the filter coefficients to unity.
    sinc1 = sinc1 / sum(sinc1)

    # Compute the frequency response using freqz (traditional method) We're computing
    # half the fftlength because freqz gives results halfway around the unit circle,
    # while the FFT method below goes all the way around.
    w1, sinc1resp_freqz = signal.freqz(sinc1, 1, fftlength/2)
    sinc1resp_freqz_dB = 20*np.log10(abs(sinc1resp_freqz))

    # You can achieve the same result as the freqz function in a more intuitive way
    # by taking an fft of the filter taps, padded out to the length
    # of the fft that you will be multiplying the response by.
    sinc1resp = abs(np.fft.fft(np.concatenate((sinc1, np.zeros(fftlength - int(sinc1.size)))))) # filter and a bunch more zeros
    sinc1resp_dB = 20*np.log10(sinc1resp)
    # now plot...
    plt.figure(fignum)
    fignum += 1
    plt.title('sinc1 frequency response from freqz (blue) and\n zero-padded FFT (red), N=' + str(n_factor))
    plt.xlabel('frequency bin')
    plt.ylabel('Rejection (dB)')
    plt.axis([0, fftlength, -50, 0])
    lines = plt.plot(sinc1resp_freqz_dB, zorder=1)
    plt.setp(lines, color='#0000FF', ls='-') #Blue
    lines = plt.plot(sinc1resp_dB)
    plt.setp(lines, color='#FF0000', ls='--') #Blue
    plt.show()

    # Example SPICE directive: .noise V(Vout2) Vin_source lin 16383 62.5 2048000
    # Arguments are output node, input node, linear spacing, # of points, bin 1 frequency, end frequency


    wide_ltc2057_psd = np.zeros(fftlength*2) # bin zero(DC) already set to zero ;)
    print('reading wide (2MHz) noise PSD data from file')
    infile = open('LTC2057_noisesim_2Meg.txt', 'r')
    print("First line (header): " + infile.readline())
    for i in range(1, fftlength*2):
        instring = infile.readline()
        indata = instring.split()         # Each line has two entries separated by a space
        wide_ltc2057_psd[i] = float(indata[1]) # Frequency Density
    infile.close()
    print('done reading!')

    #Okay now let's fold zones.
    num_zones = 4
    points_per_zone = 4096

    zones_ltc2057_psd, ltc2057_folded = fold_spectrum(wide_ltc2057_psd, points_per_zone, num_zones )

    print("Size of zones_ltc2057_psd 2d array:")
    print(len(zones_ltc2057_psd))

    plt.figure(fignum)
    fignum += 1
    plt.title("2.048MHz worth of LTC2057 noise,\nFolded into 4 Nyquist zones")
    ax = plt.gca()
    #ax.set_axis_bgcolor('#C0C0C0')
    lines = plt.plot(zones_ltc2057_psd[0])
    plt.setp(lines, color='#FF0000', ls='-') #Red
    lines = plt.plot(zones_ltc2057_psd[1])
    plt.setp(lines, color='#FF7F00', ls='--') #Orange
    lines = plt.plot(zones_ltc2057_psd[2])
    plt.setp(lines, color='#FFFF00', ls='-') #Yellow
    lines = plt.plot(zones_ltc2057_psd[3])
    plt.setp(lines, color='#00FF00', ls='--') #Green
    lines = plt.plot(ltc2057_folded)
    plt.setp(lines, color='k', ls='-') #Black
    plt.show()


    # Now multiply zones by filter response!!
    total_resp0 = list(zones_ltc2057_psd[0])
    total_resp1 = list(zones_ltc2057_psd[1])
    total_resp2 = list(zones_ltc2057_psd[2])
    total_resp3 = list(zones_ltc2057_psd[3])

    # Multipy analog filter response with the digital filter response, zone by zone
    for i in range(0, int((fftlength/2)-1)):
        total_resp0[i] = total_resp0[i] * sinc1resp[i]
        total_resp1[i] = total_resp1[i] * sinc1resp[i]
        total_resp2[i] = total_resp2[i] * sinc1resp[i]
        total_resp3[i] = total_resp3[i] * sinc1resp[i]

    # Plot LTC1563 folded response
    plt.figure(fignum)
    fignum += 1
    plt.title("LTC2057 noise to 2.048MHz, folded \nand multiplied by SINC1")
    ax = plt.gca()
    #ax.set_axis_bgcolor('#C0C0C0')
    lines = plt.plot(zones_ltc2057_psd[0])
    plt.setp(lines, color='#FF0000', ls='-') #Red
    lines = plt.plot(zones_ltc2057_psd[1])
    plt.setp(lines, color='#FF7F00', ls='--') #Orange
    lines = plt.plot(zones_ltc2057_psd[2])
    plt.setp(lines, color='#FFFF00', ls='-') #Yellow
    lines = plt.plot(zones_ltc2057_psd[3])
    plt.setp(lines, color='#00FF00', ls='--') #Green
    lines = plt.plot(ltc2057_folded)
    plt.setp(lines, color='k', ls='-') #Black
     # Plot total response of LTC1563 and digital filter on the same graph.
    lines = plt.plot(total_resp0)
    plt.setp(lines, color='#FF0000', ls='-') #Red
    lines = plt.plot(total_resp1)
    plt.setp(lines, color='#FF7F00', ls='--') #Orange
    lines = plt.plot(total_resp2)
    plt.setp(lines, color='#FFFF00', ls='-') #Yellow
    lines = plt.plot(total_resp3)
    plt.setp(lines, color='#00FF00', ls='--') #Green
    plt.show()

    #



    ltc2057_total_noise = np.zeros(fftlength*2)
    ltc2057_filtered_total_noise = np.zeros(int(fftlength/2))
    for i in range(1, int(fftlength*2)):
        ltc2057_total_noise[i] = ltc2057_total_noise[i-1] + wide_ltc2057_psd[i]
    for i in range(1, int(fftlength/2)-1):
        ltc2057_filtered_total_noise[i] = ltc2057_filtered_total_noise[i-1] + total_resp0[i] + total_resp1[i] + total_resp2[i] + total_resp3[i]

    ltc2057_total_noise = ltc2057_total_noise / ((bin_width / 2) ** 0.5)
    ltc2057_filtered_total_noise = ltc2057_filtered_total_noise  / ((bin_width / 2) ** 0.5)

    plt.figure(fignum)
    fignum += 1
    plt.title("Integrated LTC2057 noise and integrated\nnoise after filtering")
    plt.plot(ltc2057_total_noise)
    plt.plot(ltc2057_filtered_total_noise)
    plt.show()




    wide_filter = np.concatenate((sinc1resp, sinc1resp))
    wide_filtered_psd = wide_filter * wide_ltc2057_psd


    integrated_psd = integrate_psd(wide_filtered_psd, 1.0)

#
#    plt.figure(fignum)
#    fignum += 1
#    fig, ax1 = plt.subplots()
#    plt.title("LTC2057 noise vs. N=16 averaging filter")
#    ax1.plot(wide_ltc2057_psd, color='#FF0000')
#    ax1.plot(wide_filter * 0.5* np.max(wide_ltc2057_psd), color='#00FF00')
#    #ax1.plot(wide_filtered_psd)
#    ax1.set_ylabel('noise density (V/rootHz)')
#
#    ax2 = ax1.twinx()
#
#    ax2.plot(integrated_psd * 1000000.0)
#    ax2.set_ylabel('integrated noise (uV)')
#    #plt.xlim([0, 4096])
#    plt.show()
#
#    #plt.plot(wide_ltc2057_psd)
#    #plt.plot(wide_filter * np.max(wide_ltc2057_psd))
#    #plt.plot(wide_filtered_psd)
#    #plt.plot(integrated_psd)




    '''
    fig, ax1 = plt.subplots()
    t = np.arange(0.01, 10.0, 0.01)
    s1 = np.exp(t)
    ax1.plot(t, s1, 'b-')
    ax1.set_xlabel('time (s)')
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('exp', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')


    ax2 = ax1.twinx()
    s2 = np.sin(2*np.pi*t)
    ax2.plot(t, s2, 'r.')
    ax2.set_ylabel('sin', color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    plt.show()
    '''




    if(True):
        # Now for some more fun... Let's see what the total response of the digital filter and analog
        # AAF filter is. For each point on the frequency axis, a first-order analog AAF with a cutoff
        # frequency of f is multiplied by the digital filter response, then integrated across the whole axis.
        n_factor = 64
        points_per_coeff = 128
        filter_coeffs = np.ones(n_factor) / n_factor # Generate the filter
        fresp = freqz_by_fft(filter_coeffs, points_per_coeff)
        wide_filter = np.concatenate((fresp, fresp))


        factor = 16
        first_order_response = np.ndarray(len(wide_filter), dtype=float)
        product_integral = np.ndarray(int(len(wide_filter)/factor), dtype=float)
        downsampled_wide_filter = np.ndarray(len(wide_filter)//factor, dtype=float)

        print("Calculating... this could take a while :)")
        for points in range(1, len(wide_filter)//factor):
            for i in range(0, len(wide_filter)): # Generate first order response for each frequency in wide response
                cutoff = float(points*factor)
                first_order_response[i] = 1.0 / (1.0 + (i/cutoff)**2.0)**0.5 # Magnitude = 1/SQRT(1 + (f/fc)^2)
#            print ("Haven't crashed, we're on point " + str(points))
        #    plt.figure(8)
        #    plt.plot(first_order_response)
            composite_response = first_order_response * wide_filter
            datapoint = integrate_psd(composite_response, 1.0 / (n_factor))
            product_integral[points] = datapoint[len(wide_filter)-1]
            downsampled_wide_filter[points] = wide_filter[points * factor]

        product_integral_dB = 20*np.log10(product_integral)

        plt.figure(fignum)
        fignum += 1
        #plt.plot(wide_filter)
        plt.title("Total bandwidth vs. 1st order AAF bandwidth")
        plt.axis([1, 1024, 0.01, 2])
        plt.loglog(product_integral)
        plt.loglog(downsampled_wide_filter)
        plt.show()
