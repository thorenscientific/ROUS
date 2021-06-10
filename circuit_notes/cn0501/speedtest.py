import math
import pandas as pd
import time
from scipy.signal import periodogram,find_peaks,ricker
import matplotlib.pyplot as plt
import numpy as np
import os
print("Python Packages Import done")

ch = 0

vdata = []

data = [0,0,0,0,0,0,0,0] #8 channels

ch = 0

sps = [8000,16000,32000,64000,128000,256000] #available sps
buffer_len = [400,800,1024,2048,4096,8192] #test buffer lengths

buff_len =buffer_len[3]
srate = sps[5]
secrec = srate/buff_len
data[0] = np.ones(buff_len)
data[0] = data[0]*.12345
print(len(data[0]))

#print(data)

#print(secrec)

start = time.time()
for _ in range(int(secrec)):
    vdata.append(data[ch])
    print(buff_len)
end = time.time()
print(str(end-start))