# Lifted from example:
# https://docs.obspy.org/tutorial/code_snippets/seismogram_envelopes.html

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import resample

import obspy
import obspy.signal


st = obspy.read("https://examples.obspy.org/RJOB_061005_072159.ehz.new")
data = st[0].data
npts = st[0].stats.npts
samprate = st[0].stats.sampling_rate

shortdata = data[int(80*samprate):int(90*samprate)]

m2kdata = resample(shortdata, int(len(shortdata)*7500//samprate))

# Filtering the Stream object
st_filt = st.copy()
st_filt.filter('bandpass', freqmin=1, freqmax=3, corners=2, zerophase=True)

# Envelope of filtered data
data_envelope = obspy.signal.filter.envelope(st_filt[0].data)

# The plotting, plain matplotlib
plt.figure(1)
t = np.arange(0, npts / samprate, 1 / samprate)
plt.plot(t, st_filt[0].data, 'k')
plt.plot(t, data_envelope, 'k:')
plt.title(st[0].stats.starttime)
plt.ylabel('Filtered Data w/ Envelope')
plt.xlabel('Time [s]')
#plt.xlim(80, 90)
plt.show()

plt.figure(2)
plt.title("Upsampled data to send to m2k")
plt.plot(m2kdata)
plt.show