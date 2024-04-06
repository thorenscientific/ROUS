# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 15:17:26 2024

@author: Mark Thoren mark.thoren@analog.com
"""

'''
Simple script to eat CSV files exported from Osc (or any other source)
and anlyze with:
* Simple word error rate checker (ABS sample N - sample N-1) > threshold
* Sin_Params
* Save_for_Pscope (for import into Psocpe - flaky but if it doesn't crash, it works.)
* Genalyzer
'''

# %matplotlib widget # Uncomment for interactive plots in Jupyter

# Example command lines for example data files:
# python .\analyze_osc_data.py -c .\ad7385-2MSPS-M2K-1kHz-4V-p-p-2.5V-offset.csv -b 16 -r 2000000 -f 1000 -fs 5.0
# python .\analyze_osc_data.py -c .\ltc2387-18-10MSPS-M2K-10kHz-8V-p-p.csv -b 18 -r 10000000 -f 10000 -fs 8.192

import argparse
import matplotlib

import numpy as np
import genalyzer_advanced as gn
import matplotlib.pyplot as pl
import pandas as pd

from matplotlib.patches import Rectangle as MPRect
from matplotlib import pyplot as plt

from pathlib import Path

from save_for_pscope import save_for_pscope
from scipy import signal
from sin_params import sin_params

# Collect and parse arguments
parser = argparse.ArgumentParser(description="Analyze csv data from IIO Oscilloscope (or other source)")
parser.add_argument(
    "-c",
    default=['ad7385-2MSPS-M2K-1kHz-4V-p-p-2.5V-offset.csv'],
    help="-c (arg) csv filename to analyze eg: 'my_osc_file.csv'",
    action="store",
    nargs="*",
)

parser.add_argument(
    "-b",
    default=[16],
    help="-b (arg) ADC resolution (bits) eg: 16",
    action="store",
    nargs="*",
)

parser.add_argument(
    "-r",
    default=[2000000],
    help="-r (arg) sample rate in samples per second eg: 2000000",
    action="store",
    nargs="*",
)

parser.add_argument(
    "-f",
    default=[1000],
    help="-f (arg) fundamental frequency in Hz eg: 1000",
    action="store",
    nargs="*",
)

parser.add_argument(
    "-fs",
    default=[5.0],
    help="-fs (arg) adc peak-to-peak range eg: 5.0",
    action="store",
    nargs="*",
)

parser.add_argument(
    "-plt",
    default=["t"],
    help="-plt (arg) do plots, t or f eg: t",
    action="store",
    nargs="*",
)



args = parser.parse_args()
filename = args.c[0]
qres = int(args.b[0])
sampling_frequency = float(args.r[0])
fund_freq = args.f[0]
fsr = float(args.fs[0])
do_plots = {'t':True, 'f':False}[args.plt[0]]

filename_with_path = Path(__file__).with_name(filename)

print("matplotlib version: ", matplotlib.__version__)
print("analyzing file: ", filename)

dataframe = pd.read_csv(filename_with_path, header=None)
data = dataframe[0].tolist()

# Quick hack for Pscope, not robust (bipolar device with a small positive offset
#  and very low signal level could detect as unipolar) 
if min(data) < 0:
    is_bipolar = True
    print("Data is bipolar...")
else:
    is_bipolar = False
    print("Data seems to be unipolar...")

print("Saving out .adc file for Pscope...")    
save_for_pscope(filename_with_path.with_suffix('.adc'), qres, is_bipolar, len(data), "DC0000", "LTC1111", data, data, )

nfft = len(data)
navg = 1
data_nodc = data - np.average((data)) # Strip out DC
voltage = (data_nodc * fsr) / (2.0**qres)

# Plot analog waveform
if do_plots is True:
    pl.figure(1)
    plt.clf()
    pl.title("Raw ADC codes")
    pl.plot(data)
    pl.tight_layout()
    pl.show()

# Plot waveform converted to voltage
if do_plots is True:
    x = np.arange(0, len(data))
    plt.figure(2)
    plt.clf()
    plt.title("ADC Voltage, from raw codes, Vref (DC removed)")
    plt.plot(x, voltage)
    pl.tight_layout()
    plt.show()

f, Pxx_spec = signal.periodogram(voltage , sampling_frequency, window = "blackman", scaling = "spectrum")
Pxx_abs = np.sqrt(Pxx_spec)

if do_plots is True:
    plt.figure(3)
    plt.clf()
    plt.title("FFT from SciPy periodogram, spectrum scaling")
    plt.semilogy(f, Pxx_abs)
    plt.ylim([1e-7, 5])
    plt.xlabel("frequency [Hz]")
    plt.ylabel("Voltage(V)")
    pl.tight_layout()
    plt.draw()
    plt.pause(0.05)
    plt.show()



# Saving time_domaine twice - workaround because save_for_pscope expects two channels
# save_for_pscope("ltc2387_data.adc", 18, True, len(data), "DC0000", "LTC1111", data, data, )

harmonics, snr, thd, sinad, enob, sfdr, floor = sin_params(data)
print("##########################################################")
print("################# Sin Params Results #####################")
print("##########################################################")
print("A.C. Performance parameters (ONLY valid for a sine input):")
print("Harmonics:", harmonics)
print("snr: ", snr)
print("THD: ", thd)
print("Sinad: ", sinad)
print("ENOB: ", enob)
print("SFDR: ", sfdr)
print("Noise Floor: ", floor)
print("\n\n")


# Set up Genalyzer parameters

code_fmt = gn.CodeFormat.TWOS_COMPLEMENT  # ADC codes format
rfft_scale = gn.RfftScale.DBFS_SIN  # FFT scale
# window = gn.Window.NO_WINDOW  # FFT window
window = gn.Window.BLACKMAN_HARRIS  # FFT window

ssb_fund = 4  # Single side bin fundamental
ssb_rest = 5
# If we are not windowing then choose the closest coherent bin for fundamental
if gn.Window.NO_WINDOW == window:
    fund_freq = gn.coherent(nfft, sampling_frequency, fund_freq)
    ssb_fund = 0
    ssb_rest = 0

# Compute FFT
fft_cplx = gn.rfft(np.array(data), qres, navg, nfft, window, code_fmt, rfft_scale)
# Compute frequency axis
freq_axis = gn.freq_axis(nfft, gn.FreqAxisType.REAL, sampling_frequency)
# Compute FFT in db
fft_db = gn.db(fft_cplx)

# Fourier analysis configuration
key = 'fa'
gn.mgr_remove(key)
gn.fa_create(key)
gn.fa_analysis_band(key, "fdata*0.0", "fdata*1.0")
gn.fa_fixed_tone(key, 'A', gn.FaCompTag.SIGNAL, fund_freq, ssb_fund)
gn.fa_hd(key, 4)
gn.fa_ssb(key, gn.FaSsb.DEFAULT, ssb_rest)
gn.fa_ssb(key, gn.FaSsb.DC, -1)
gn.fa_ssb(key, gn.FaSsb.SIGNAL, -1)
gn.fa_ssb(key, gn.FaSsb.WO, -1)
gn.fa_fsample(key, sampling_frequency)

print("##########################################################")
print("################# Genalyzer Results #####################")
print("##########################################################")

# print(gn.fa_preview(key, False))

# Fourier analysis results
fft_results = gn.fft_analysis(key, fft_cplx, nfft)
# compute THD. Double-check the math, thd_rss is with respect to full-scale
# so subtracting full-scale amplitude
thd = 20*np.log10(fft_results['thd_rss']) - fft_results['A:mag_dbfs']
print("\nFourier Analysis Results:")
print("\nFrequency, Phase and Amplitude for Harmonics:\n")
for k in ['A:freq', 'A:mag_dbfs', 'A:phase',
          '2A:freq', '2A:mag_dbfs', '2A:phase',
          '3A:freq', '3A:mag_dbfs', '3A:phase',
          '4A:freq', '4A:mag_dbfs', '4A:phase']:
    print("{:20s}{:20.6f}".format(k, fft_results[k]))
print("\nFrequency, Phase and Amplitude for Noise:\n")
for k in ['wo:freq','wo:mag_dbfs', 'wo:phase']:
    print("{:20s}{:20.6f}".format(k, fft_results[k]))
print("\nSNR and THD:")
for k in ['snr', 'fsnr']:
    print("{:20s}{:20.6f}".format(k, fft_results[k]))
print("{:20s}{:20.6f}".format("thd", thd))

# Plot FFT
if do_plots is True:
    pl.figure(4)
    fftax = pl.subplot2grid((1, 1), (0, 0), rowspan=2, colspan=2)
    pl.title("Genalyzer FFT")
    pl.plot(freq_axis, fft_db)
    pl.grid(True)
    # pl.xlim(freq_axis[0], 20)
    pl.ylim(-160.0, 20.0)
    annots = gn.fa_annotations(fft_results)
    
    for x, y, label in annots["labels"]:
        pl.annotate(label, xy=(x, y), ha='center', va='bottom')
    for box in annots["tone_boxes"]:
        fftax.add_patch(MPRect((box[0], box[1]), box[2], box[3],
                               ec='pink', fc='pink', fill=True, hatch='x'))
    
    pl.tight_layout()
    pl.show()
