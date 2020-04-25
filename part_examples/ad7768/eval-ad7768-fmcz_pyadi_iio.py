'''
AD7768-FMCZ Zedboard data capture, plot, save module

Provides a single functon that returns a list of lists of individual channel data
Optionally analyzes and plots all channels and / or save data to a file

testdata = eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=True, do_plot = True,
                             do_write_to_file = True)

ToDo - add options for ADC sample rate and ADC filter type
Note that filter type is not supported in the Linux driver yet.
'''

def eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=True, do_plot = True,
                             do_write_to_file = True):
    import sys
    import numpy as np

    try:
        import iio
    except:
        print ("iio not found!")
        sys.exit(0)

    buflen = NUM_SAMPLES

    try:
        ctx = iio.Context(my_ip)
    except:
        print("No device found")
        sys.exit(0)

    #clock = ctx.find_device("ad9571-4")
    rxadc = ctx.find_device("ad7768") # RX/ADC Core in HDL for DMA

    v0 = rxadc.find_channel("voltage0") # Find individual channels
    v1 = rxadc.find_channel("voltage1")
    v2 = rxadc.find_channel("voltage2")
    v3 = rxadc.find_channel("voltage3")
    v4 = rxadc.find_channel("voltage4")
    v5 = rxadc.find_channel("voltage5")
    v6 = rxadc.find_channel("voltage6")
    v7 = rxadc.find_channel("voltage7")

    v0.enabled = True # Enable individual channels
    v1.enabled = True
    v2.enabled = True
    v3.enabled = True
    v4.enabled = True
    v5.enabled = True
    v6.enabled = True
    v7.enabled = True
    # Create buffer
    rxbuf = iio.Buffer(rxadc, buflen, False) # False = non-cyclic buffer

    for j in range(5): #Flush buffers. To Do: what's the default number?
        rxbuf.refill()
        x = rxbuf.read()
    # got our data, clean up...
    del rxbuf
    del ctx

    #get data from buffer (signed 24-bit data, right justified in a 32-bit word)
    data = np.frombuffer(x, np.int32)

    #split data into respective channels
    ch_data = [data[0::8],data[1::8],data[2::8],data[3::8],
               data[4::8],data[5::8],data[6::8],data[7::8]]
    if do_plot == True:
        import llt.common.functions as llt_fns
        llt_fns.plot_channels(24,
                        *ch_data,
                        verbose=False)
    return ch_data

if __name__ == '__main__':
    import sys
    NUM_SAMPLES = 8 * 1024
    buflen = 8192
    hardcoded_ip = 'ip:10.26.148.119' #118
    my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip

    # to use this function in your own code to just grab samples, you would
    # typically do:
    # eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=False, do_plot = False,
    #                        do_write_to_file = False)
    testdata = eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=True, do_plot = False,
                             do_write_to_file = True)