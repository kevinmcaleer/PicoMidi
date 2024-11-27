from machine import Pin, PWM, ADC, Timer
import time

# Define Pins
PWM_PIN = 16  # GPIO for audio output
LDR_PIN = 28  # ADC pin for the LDR
BUTTON_PIN = 14  # GPIO for button input
LED_PIN = 25  # Built-in LED
LDR_LED_PIN = 15  # GPIO for LDR LED

# Initialize Pins
pwm_out = PWM(Pin(PWM_PIN))
pwm_out.freq(31250)  # Audio frequency (31.25kHz)

ldr_adc = ADC(LDR_PIN)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT)
ldr_led = Pin(LDR_LED_PIN, Pin.OUT)

# Variables
sync_phase_acc = 0
sync_phase_inc = 0
grain_phase_acc = 0
grain_phase_inc = 0
grain_amp = 0x7FFF
grain_decay = 0
grain2_phase_acc = 0
grain2_phase_inc = 0
grain2_amp = 0x7FFF
grain2_decay = 0

ldr_min = 1023
ldr_max = 0
ldr_value = 0
map_mode = 0
ldr_switch_state = False

# Helper Functions
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def triangle_wave(phase):
    value = (phase >> 7) & 0xFF
    if phase & 0x8000:
        value = ~value & 0xFF
    return value

# Button handling
def button_pressed(pin):
    global map_mode
    map_mode = (map_mode + 1) % 6  # Cycle through modes
    led.toggle()

button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# LDR Calibration
def calibrate_ldr():
    global ldr_min, ldr_max
    led.value(1)
    print('Calibrating')
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
        value = ldr_adc.read_u16() >> 6  # Scale to 10-bit
        ldr_min = min(ldr_min, value)
        ldr_max = max(ldr_max, value)
    led.value(0)
    print('Calibration complete')
    
calibrate_ldr()

# Audio Generation
def audio_timer_callback(timer):
    global sync_phase_acc, grain_phase_acc, grain_phase_inc, grain_amp
    global grain2_phase_acc, grain2_phase_inc, grain2_amp, grain_decay, grain2_decay

    # Synchronize phases
    sync_phase_acc += sync_phase_inc
    if sync_phase_acc < sync_phase_inc:
        grain_phase_acc = 0
        grain_amp = 0x7FFF
        grain2_phase_acc = 0
        grain2_amp = 0x7FFF

    # Increment grain phases
    grain_phase_acc += grain_phase_inc
    grain2_phase_acc += grain2_phase_inc

    # Generate triangle wave and apply decay
    output = triangle_wave(grain_phase_acc) * (grain_amp >> 8)
    output += triangle_wave(grain2_phase_acc) * (grain2_amp >> 8)

    grain_amp -= (grain_amp >> 8) * grain_decay
    grain2_amp -= (grain2_amp >> 8) * grain2_decay

    # Clip and scale output
    output = max(0, min(255, output >> 9))
    pwm_out.duty_u16(output << 8)  # Scale to 16-bit for MicroPython PWM

# Timer for audio generation
audio_timer = Timer()
audio_timer.init(freq=31250, mode=Timer.PERIODIC, callback=audio_timer_callback)

# Main Loop
while True:
    # Read LDR
    ldr_value = ldr_adc.read_u16() >> 6  # Scale to 10-bit
    ldr_value = map_value(ldr_value, ldr_min, ldr_max, 0, 1023)

    # Update phase increments and decay based on inputs
    sync_phase_inc = map_value(ldr_value, 0, 1023, 0, 65535)
    grain_phase_inc = map_value(ldr_value, 0, 1023, 0, 32767)
    grain_decay = ldr_value >> 8
    grain2_phase_inc = grain_phase_inc
    grain2_decay = grain_decay

    # Toggle LDR LED based on value
    ldr_led.value(ldr_value > 512)
    print(f"ldr value: {ldr_value}")
    time.sleep(0.01)  # Small delay to reduce CPU usage
