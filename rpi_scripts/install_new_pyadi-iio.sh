#!/bin/bash

sudo pip3 uninstall -y pyadi-iio

git clone https://github.com/analogdevicesinc/pyadi-iio.git
cd pyadi-iio
git checkout master
sudo python3 setup.py install