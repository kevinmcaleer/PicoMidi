from machine import ADC, PWM, Pin
from time import sleep

# Define pins
output_pin = 16  # Output for PWM
pwm_pin = 28  # Input ADC for frequency
pwm_pin2 = 27  # Input ADC for duty cycle

# Initialize hardware
pwm_input = ADC(pwm_pin)
pwm_input2 = ADC(pwm_pin2)
output = PWM(Pin(output_pin))

# Define frequency range and quantization steps
min_frequency = 10  # Minimum frequency (Hz)
max_frequency = 200  # Maximum frequency (Hz)
frequency_quantization_step = 10  # Frequency step size (Hz)

# Define duty cycle quantization
min_duty = 0  # Minimum duty cycle (0%)
max_duty = 65535  # Maximum duty cycle (100%)
duty_quantization_step = 8192  # Quantize duty in 6.25% steps

print(f'Frequency quantization step: {frequency_quantization_step}')
print(f'Duty cycle quantization step: {duty_quantization_step}')

# Initialize PWM output with a default duty cycle
output.duty_u16(32768)  # 50% duty cycle

# Map function
def map_value(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Main loop
while True:
    # Read ADC values
    raw_pwm_value = pwm_input.read_u16()
    raw_duty_value = pwm_input2.read_u16()
    
    # Map the ADC values to the desired ranges
    mapped_frequency = map_value(raw_pwm_value, 0, 65535, min_frequency, max_frequency)
    mapped_duty = map_value(raw_duty_value, 0, 65535, min_duty, max_duty)
    
    # Quantize the frequency and duty cycle
    quantized_frequency = (mapped_frequency // frequency_quantization_step) * frequency_quantization_step
    quantized_duty = (mapped_duty // duty_quantization_step) * duty_quantization_step
    
    # Update PWM output
    output.freq(quantized_frequency)  # Set quantized frequency
    output.duty_u16(quantized_duty)  # Set quantized duty cycle
    
    # Print debug information
    print(f"Quantized Frequency: {quantized_frequency}, Quantized Duty Cycle: {quantized_duty}, Raw Duty: {raw_duty_value}")
    
    # Small delay for loop stability
    sleep(0.05)
