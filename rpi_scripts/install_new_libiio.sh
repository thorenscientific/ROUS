#!/bin/bash

git clone https://github.com/analogdevicesinc/libiio.git
cd libiio
git checkout master
mkdir build && cd build && cmake -DWITH_SYSTEMD=ON -DWITH_HWMON=ON -DWITH_EXAMPLES=ON ../ && make && sudo make install
