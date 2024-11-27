from machine import ADC, PWM, Pin
from time import sleep

output_pin = 16
pwm_pin = 28
pwm_pin2 = 27

pwm_input = ADC(pwm_pin)
pwm_input2 = ADC(pwm_pin2)
output = PWM(Pin(output_pin))

base_frequency = 5000
tone = 0 # 10khz

pwm_value = 0
output.duty_u16(20000)

def map_values()


while True:
    output.duty_u16(pwm_input2.read_u16())
    pwm_value = pwm_input.read_u16()
    tone = base_frequency + pwm_value
    print(f"tone is {tone}, pwm_value is {pwm_value}")
    output.freq(tone)
    sleep(0.01)
