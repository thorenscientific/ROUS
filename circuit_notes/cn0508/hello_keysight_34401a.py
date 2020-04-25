# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 17:58:06 2019

@author: MThoren
"""

import visa
from llt.utils.hp_multimeters import *


rm = resource_manager()
hp34401a = rm.open_resource("GPIB0::22::INSTR", timeout = 50000)

#hp34401a_lcd_disp(hp34401a, "*CLS")
#hp34401a_lcd_disp(hp34401a, "hello")

print(hp34401a_read_voltage(hp34401a))


hp34401a.timeout = 5000
hp34401a.write("*CLS")  # Clear the LCD screen
hp34401a.write("*IDN?") # Read the ID name command for the meter
print("Voltage:")
print (hp34401a.read())   # Display the ID name


