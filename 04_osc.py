from machine import ADC, PWM, Pin
from time import ticks_ms, sleep_ms
import math

# Define pins
output_pin = 16  # Output for PWM
osc1_pin = 28  # ADC for Oscillator 1 frequency
osc2_pin = 27  # ADC for Oscillator 2 frequency

# Initialize hardware
osc1_input = ADC(osc1_pin)
osc2_input = ADC(osc2_pin)
output = PWM(Pin(output_pin))

# Define waveform types
WAVEFORMS = ["sine", "square", "triangle", "sawtooth"]
waveform_index = 0  # Default to sine wave

# Define frequency range
min_frequency = 440  # Minimum frequency (Hz)
max_frequency = 880  # Maximum frequency (Hz)
frequency_quantization_step = 1  # Quantize frequency in 50 Hz steps

# PWM settings
output.duty_u16(32768)  # 50% duty cycle
output.freq(440)  # Default frequency

# Generate waveform values
def generate_waveform(waveform, phase):
    """Generate waveform value based on type and phase."""
    if waveform == "sine":
        return int(32768 + 32767 * math.sin(2 * math.pi * phase))
    elif waveform == "square":
        return 65535 if phase < 0.5 else 0
    elif waveform == "triangle":
        return int(65535 * (2 * phase) if phase < 0.5 else 65535 * (2 - 2 * phase))
    elif waveform == "sawtooth":
        return int(65535 * phase)
    return 0  # Default to 0 if waveform type is invalid

# Map function
def map_value(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Timing
last_waveform_switch_time = ticks_ms()  # Track the last waveform switch time
waveform_switch_interval = 10000  # Switch waveforms every 10 seconds

# Main loop
phase_osc1 = 0
phase_osc2 = 0
phase_increment_osc1 = 0
phase_increment_osc2 = 0
sampling_rate = 8000  # 8 kHz sampling rate for waveforms
while True:
    # Read ADC values
    raw_osc1_value = osc1_input.read_u16()
    raw_osc2_value = osc2_input.read_u16()
    
    # Map ADC values to frequencies
    freq_osc1 = map_value(raw_osc1_value, 0, 65535, min_frequency, max_frequency)
    freq_osc2 = map_value(raw_osc2_value, 0, 65535, min_frequency, max_frequency)
    
    # Quantize frequencies
    quantized_freq_osc1 = (freq_osc1 // frequency_quantization_step) * frequency_quantization_step
    quantized_freq_osc2 = (freq_osc2 // frequency_quantization_step) * frequency_quantization_step
    
    # Calculate phase increment for each oscillator
    phase_increment_osc1 = quantized_freq_osc1 / sampling_rate
    phase_increment_osc2 = quantized_freq_osc2 / sampling_rate
    
    # Generate waveform samples
    phase_osc1 = (phase_osc1 + phase_increment_osc1) % 1.0
    phase_osc2 = (phase_osc2 + phase_increment_osc2) % 1.0
    sample_osc1 = generate_waveform(WAVEFORMS[waveform_index], phase_osc1)
    sample_osc2 = generate_waveform(WAVEFORMS[waveform_index], phase_osc2)
    
    # Mix the two oscillators (simple average for now)
    mixed_sample = (sample_osc1 + sample_osc2) // 2
    
    # Output to PWM
    output.duty_u16(mixed_sample)
    
    # Check if it's time to switch waveforms
    current_time = ticks_ms()
    if current_time - last_waveform_switch_time > waveform_switch_interval:
        last_waveform_switch_time = current_time
        waveform_index = (waveform_index + 1) % len(WAVEFORMS)  # Cycle through waveforms
    
    # Print debug information
    print(f"Osc1: {quantized_freq_osc1} Hz, Osc2: {quantized_freq_osc2} Hz, Waveform: {WAVEFORMS[waveform_index]}")
    
    # Small delay for stability
    sleep_ms(1)  # 1 ms delay to approximate the sampling rate
