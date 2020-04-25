#window Cmd
#C:\Uses\ereyta>iio_info -u ip:192.168.1.100


import sys
import numpy as np
import time

sys.path.append('')
import iio


def main(my_ip):
    #ctx = iio.Context('local:') # "local" is what you would use if you were running this script directly on the Raspberry Pi.
                                 # To run over a network connection, run iiod on the Pi, then give the Pi's address as shown next...


#    freq_out = 4000000000 #frequency output set at 4GHz
#    freq_out = 122880000 #set frequency output at 10Hz for spectral purity test   
#    freq_out = 100 #set frequency output at 100Hz for spectral purity test  
    freq_out = 100000000 #set frequency output at 100MHz for spectral purity test   
#    freq_out = 500000000 #set frequency output at 500MHz for spectral purity test   
#    freq_out = 900000000 #set frequency output at 900MHz for spectral purity test   
#    freq_out = 1000000000 #set frequency output at 1GHz for spectral purity test   
#    freq_out = 1800000000 #set frequency output at 1.8GHz for spectral purity test   
#    freq_out = 2000000000 #set frequency output at 2GHz for spectral purity test   
#    freq_out = 3000000000 #set frequency output at 3GHz for spectral purity test  
#    freq_out = 3600000000 #set frequency output at 3.6GHz for spectral purity test 
#    freq_out = 4000000000 #set frequency output at 4GHz for spectral purity test 
#    freq_out = 4500000000 #set frequency output at 4.5GHz for spectral purity test         
#    freq_out = 5000000000 #set frequency output at 5GHz for spectral purity test         
                            

    sampling_rate = 5000000000 #6000 MHz
#    sampling_rate = 5898240000 #5898.24MHz
#    sampling_rate = 6000000000 #6000 MHz

#    sampling_rate = freq_out * 2
    
    print(str(my_ip))
    ctx = iio.Context(my_ip)
    if ctx == None:
        print("context not found")
        return (-1)


    amp=ctx.find_device("ad9166-amp")
    ad9166=ctx.find_device("ad9166")


# enable the amp
    amp.attrs["en"].value="1"

# to enable full scale amplitude
    scale = ad9166.find_channel ("altvoltage0",True)
    scale.attrs["raw"].value = "32767" #full scale n =15
#    scale.attrs["raw"].value = "16383" #mid scale n =14
#    scale.attrs["raw"].value = "4095" #mid scale n =12
#    scale.attrs["raw"].value = "2047" #mid scale n =11

#read and write to the sampling frequency 
    print (ad9166.attrs["sampling_frequency"].value)  
    ad9166.attrs["sampling_frequency"].value = str(sampling_rate)
    print (ad9166.attrs["sampling_frequency"].value) 
    
#read the address 0x111  
    print (ad9166.debug_attrs["direct_reg_access"].value)  
    
#write 0x41 to register 0x111 to enable FIR85 
    ad9166.debug_attrs["direct_reg_access"].value = "0x111 0x41"
 
#set single value frequency output
    scale.attrs["nco_frequency"].value = str(freq_out)

#test the Modulation Stimulus
    scale.attrs["raw"].value = "10" #full scale n =15   
    time.sleep(3)
    scale.attrs["raw"].value = "32767" #full scale n =15
#    scale.attrs["raw"].value = "10" #full scale n =15

    print ("done")
    print (freq_out)
    print (scale.attrs["raw"].value)

#sweep frequency output
#for val in range(start,end,interval)
#    for freq_out in range(10000000,3500000000,10000000):   
#   for freq_out in range(100000000,5500000000,10000000):   
#        print(freq_out)
#        scale.attrs["nco_frequency"].value = str(freq_out)
#        time.sleep(1)
  

if __name__ == '__main__':
    import sys
#    hardcoded_ip = 'ip:10.116.171.114' #118
#    hardcoded_ip = 'ip:10.116.177.62' #118
#    hardcoded_ip = 'ip:10.116.177.57' #118
    hardcoded_ip = 'ip:192.168.1.100' #118

    my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip

    testdata = main(my_ip)
    
