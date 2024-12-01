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
frequency_quantization_step = 2  # Frequency step size (Hz)

# Define duty cycle quantization
min_duty = 0  # Minimum duty cycle (0%)
max_duty = 65535  # Maximum duty cycle (100%)
duty_quantization_step = 8192  # Quantize duty in 6.25% steps

# Initialize filter variables
frequency_lpf = 0  # Initial smoothed frequency
duty_cycle_lpf = 0  # Initial smoothed duty cycle
alpha = 0.1  # Smoothing factor (lower = smoother, higher = more responsive)

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
    
    # Apply low-pass filter
    frequency_lpf = (alpha * mapped_frequency) + ((1 - alpha) * frequency_lpf)
    duty_cycle_lpf = (alpha * mapped_duty) + ((1 - alpha) * duty_cycle_lpf)
    
    # Quantize the filtered frequency and duty cycle
    quantized_frequency = (int(frequency_lpf) // frequency_quantization_step) * frequency_quantization_step
    quantized_duty = (int(duty_cycle_lpf) // duty_quantization_step) * duty_quantization_step
    
    # Update PWM output
    output.freq(quantized_frequency)  # Set quantized frequency
    output.duty_u16(quantized_duty)  # Set quantized duty cycle
    
    # Print debug information
    print(f"Quantized Frequency: {quantized_frequency}, Quantized Duty Cycle: {quantized_duty}, "
          f"Filtered Frequency: {frequency_lpf:.2f}, Filtered Duty: {duty_cycle_lpf:.2f}")
    
    # Small delay for loop stability
    sleep(0.05)
