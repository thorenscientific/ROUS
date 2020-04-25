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
        import adi
    except:
        print ("pyadi-iio not found!")
        sys.exit(0)

    buflen = NUM_SAMPLES

    try:
        myadc=adi.ad7768()
    except:
        print("No device found")
        sys.exit(0)

    ch_data = myadc.rx()
    del myadc

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
    hardcoded_ip = 'ip:10.26.148.118' #118
    my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip

    # to use this function in your own code to just grab samples, you would
    # typically do:
    # eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=False, do_plot = False,
    #                        do_write_to_file = False)
    testdata = eval_ad7768_fmcz(my_ip, NUM_SAMPLES, verbose=True, do_plot = False,
                             do_write_to_file = True)