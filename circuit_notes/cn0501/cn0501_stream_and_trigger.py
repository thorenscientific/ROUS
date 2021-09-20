# Copyright (C) 2021 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTIT11111111111111111111111111111111111111111111111111111111111111111111UTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
Some Matplotlib Animation Tutorials:
https://towardsdatascience.com/animations-with-matplotlib-d96375c5442c
'''


import argparse
import sys
import threading
import time
from queue import Full, Queue

import adi
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui
from pyqtgraph.Qt import QtCore, QtGui
from scipy import signal
from scipy.fftpack import fft



class ADIPlotter(object):
    def __init__(self, classname, uri):
        self.yrange = 2**14
        self.q = Queue(maxsize=20)
        self.stream = eval("adi." + classname + "(uri='" + uri + "')")
#        self.stream.sample_rate = 10000000
        self.stream.sample_rate = 8000

        self.stream.power_mode = "FAST_MODE" #FAST_MODE MEDIAN_MODE LOW_POWER_MODE
        self.stream.filter = "WIDEBAND"
        self.stream.sample_rate = 8000
        self.stream.rx_buffer_size = 16384

#        self.stream.rx_lo = 1000000000
#        self.stream.tx_lo = 1000000000
#        self.stream.dds_single_tone(3000000, 0.9)
#        self.stream.rx_buffer_size = 2 ** 12
#        self.stream.rx_enabled_channels = [7]

        pg.setConfigOptions(antialias=True)
        self.traces = {}
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title="CN0501 Recorder")
        self.win.setWindowTitle("CN0501 Recorder")
        self.win.setGeometry(5, 115, 1910, 1070)

        wf_xaxis = pg.AxisItem(orientation="bottom")
        wf_xaxis.setLabel(units="Seconds")

        wf_ylabels = [(-1.0 * self.yrange, "-16384"), (0, "0"), (self.yrange, "16384")]
        wf_yaxis = pg.AxisItem(orientation="left")
        wf_yaxis.setTicks([wf_ylabels])

        sp_xaxis = pg.AxisItem(orientation="bottom")
        sp_xaxis.setLabel(units="Hz")

        self.waveform = self.win.addPlot(
            title="WAVEFORM", row=1, col=1, axisItems={"bottom": wf_xaxis},
        )
#        self.spectrum = self.win.addPlot(
#            title="SPECTRUM", row=2, col=1, axisItems={"bottom": sp_xaxis},
#        )
        self.waveform.showGrid(x=True, y=True)
#        self.spectrum.showGrid(x=True, y=True)

        # waveform and spectrum x points
        self.x = np.arange(0, self.stream.rx_buffer_size) / self.stream.sample_rate
        self.f = np.linspace(
            -1 * self.stream.sample_rate / 2,
            self.stream.sample_rate / 2,
            self.stream.rx_buffer_size,
        )

        self.counter = 0
        self.min = -100
        self.window = signal.kaiser(self.stream.rx_buffer_size, beta=38)

        self.run_source = True
        self.thread = threading.Thread(target=self.source)
        self.thread.start()


    def source(self):
        print("Thread running")
        while self.run_source:
            data = self.stream.rx() # [0] okay, try stuffing all data in!
            print("got this many samples: ", len(data[0]))
            try:
                self.q.put(data, block=False, timeout=4)
            except Full:
                continue

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == "ch0":
                self.traces[name] = self.waveform.plot(color="b", pen="c", width=3)
                self.waveform.setYRange(-(self.yrange) - 200, self.yrange + 200, padding=0)
                self.waveform.setXRange(
                    0,
                    self.stream.rx_buffer_size / self.stream.sample_rate,
                    padding=0.005,
                )

            if name == "ch1":
                self.traces[name] = self.waveform.plot(color="r",pen="c", width=3)
                self.waveform.setYRange(-(self.yrange) - 200, self.yrange + 200, padding=0)
                self.waveform.setXRange(
                    0,
                    self.stream.rx_buffer_size / self.stream.sample_rate,
                    padding=0.005,
                )

            if name == "ch2":
                self.traces[name] = self.waveform.plot(color="r",pen="c", width=3)
                self.waveform.setYRange(-(self.yrange) - 200, self.yrange + 200, padding=0)
                self.waveform.setXRange(
                    0,
                    self.stream.rx_buffer_size / self.stream.sample_rate,
                    padding=0.005,
                )


    def update(self):
        while not self.q.empty():
            all_data = self.q.get() # This is now all channels!
            wf_data = all_data[0] #self.q.get() Extract only first channel so we
            print("examining data...") # don't break anything downstream (to be updated)
            dmin = np.min(wf_data)
            dmax = np.max(wf_data)
            print("minimum: ", dmin)
            print("maximum: ", dmax)
            if abs(dmax - dmin) > 0.0000001:
                print("Trigger condition met!")
                self.set_plotdata(
                    name="ch0", data_x=self.x, data_y=np.real(wf_data),
                )
            self.set_plotdata(
                    name="ch1", data_x=self.x, data_y=np.real(all_data[1]),
                )
            self.set_plotdata(
                    name="ch2", data_x=self.x, data_y=np.real(all_data[2]),
                )
#                sp_data = np.fft.fft(wf_data)
#                sp_data = np.abs(np.fft.fftshift(sp_data)) / self.stream.rx_buffer_size
#                sp_data = 20 * np.log10(sp_data / (2 ** 11))
#                self.set_plotdata(name="spectrum", data_x=self.f, data_y=sp_data)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1)
        self.start()
        self.run_source = False


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="ADI fast plotting app")
    parser.add_argument(
        "class", help="pyadi class name to use as plot source", action="store"
    )
    parser.add_argument("uri", help="URI of target device", action="store")
    args = vars(parser.parse_args())

    if args["class"] not in ["Pluto", "ad9361", "ad9364", "ad9363", "ad7768"]:
        raise Exception("Only AD936x based devices supported")

    app = ADIPlotter(args["class"], args["uri"])
    app.animation()
    app.thread.join()
