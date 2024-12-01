from machine import ADC
import time

# Plug a potentiometer into Pin 28 of the Pico (the middle pin is the signal pin to the Pico)
# The potentiometer also needs 3.3v and Gnd pins connecting
#  
# VCC --| 
#        -----
# SIG --|     | 
#        -----
# GND --|


# Initialize the ADC for the temperature sensor
sensor_adc = ADC(28)

while True:
    # Read the raw ADC value
    raw_value = sensor_adc.read_u16()
    print(f"ADC: {raw_value}")
    time.sleep(0.2)