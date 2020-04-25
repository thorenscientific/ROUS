import sys
import numpy as np
import time

sys.path.append('')
import iio


def main(my_ip):
    #ctx = iio.Context('local:') # "local" is what you would use if you were running this script directly on the Raspberry Pi.
                                 # To run over a network connection, run iiod on the Pi, then give the Pi's address as shown next...
    freq_out = 1000000000
    print(str(my_ip))
    ctx = iio.Context(my_ip)
    if ctx == None:
        print("context not found")
        return (-1)

# enable the amp
    amp=ctx.find_device("ad9166-amp")
    amp.attrs["en"].value="1"

# to enable full scale amplitude
    ad9166=ctx.find_device("ad9166")
    scale = ad9166.find_channel ("altvoltage0",True)
    scale.attrs["raw"].value = "32767"
    
#read the address 0x111  
    print (ad9166.debug_attrs["direct_reg_access"].value)  
    
#write 0x41 to register 0x111 to enable FIR85 
    ad9166.debug_attrs["direct_reg_access"].value = "0x111 0x41"
    
    scale.attrs["nco_frequency"].value = str(freq_out)
 #   for freq_out in range(10000000,1000000000,10000000):   
 #       print(freq_out)
 #    scale.attrs["nco_frequency"].value = str(freq_out)
 #       time.sleep(5)

if __name__ == '__main__':
    import sys
    hardcoded_ip = 'ip:10.116.171.114' #118
    my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip

    testdata = main(my_ip)