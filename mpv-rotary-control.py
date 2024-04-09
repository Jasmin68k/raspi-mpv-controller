# Configure rotary encoder pin assignments and mpv-socket paths in main function

# To be compatible with Raspberry Pi 5 and kernels >=6.6.0 we're using the
# rpi-lgpio package, since in those cases raw RPi.GPIO is broken.

# Remove python3-rpi.gpio:
# sudo apt-get purge python3-rpi.gpio
# Requires Python package rpi-lgpio
# Install python3-rpi-lgpio:
# sudo apt-get install python3-rpi-lgpio

# To run this script
# Run script:
# python /path/to/mpv-rotary-control.py
# Exit with CTRL-C

import RPi.GPIO as GPIO
import socket
import json
from time import sleep

def send_command(socket_path, command):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)
        command = json.dumps(command).encode('utf-8') + b'\n'
        sock.sendall(command)
        response = sock.recv(1024)
        return response

def toggle_mute(socket_path):
    command = {"command": ["osd-msg-bar", "cycle", "mute"]}
    return send_command(socket_path, command)

def change_volume(socket_path, change):
    command = {"command": ["osd-msg-bar", "add", "volume", change]}
    return send_command(socket_path, command)

class RotaryEncoder:
    def __init__(self, encoder_name, socket_path, clk_pin, dt_pin, sw_pin):
        self.encoder_name = encoder_name
        self.socket_path = socket_path
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.sw_pin = sw_pin
        self.clkLastState = None
        self.setup()

        print(f"'{self.encoder_name}' is active on socket: {self.socket_path}")

    def setup(self):
        GPIO.setup(self.clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor
        # bounce delay on rotation usually not needed, add otherwise
        GPIO.add_event_detect(self.clk_pin, GPIO.BOTH, callback=self.rotary_interrupt)
        # bounce delay for push button to prevent erroneous detection of multiple button presses
        GPIO.add_event_detect(self.sw_pin, GPIO.FALLING, callback=self.button_pressed, bouncetime=250)

    def rotary_interrupt(self, channel):
        clkState = GPIO.input(self.clk_pin)
        dtState = GPIO.input(self.dt_pin)

        if clkState != self.clkLastState:
            if dtState != clkState:
                change_volume(self.socket_path, 1)
            else:
                change_volume(self.socket_path, -1)
        self.clkLastState = clkState

    def button_pressed(self, channel):
        toggle_mute(self.socket_path)

if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)

        # Initialize encoders with names,
        # paths to mpv-sockets and
        # clk, dt and sw GPIO #s.
        # Note that GPIO #s != pin #s on Raspberry Pi.
        # Used here:
        # clk: GPIO 24, 23, 25 = pins 18, 13, 37
        # dt: GPIO 23, 17, 22 = pins 16, 11, 31
        # sw: GPIO 26, 6, 16 = pins 22, 15, 36
        # For ground (GND) you can use f. e. pins 14, 9, 34.
        # For voltage most rotary encoders work with 5V or 3.3V.
        # F. e. 5V pins 2, 4 - 3.3V pin 17
        encoders = [
            RotaryEncoder("Rotary encoder 1", '/tmp/mpv-1', 24, 23, 25),
            RotaryEncoder("Rotary encoder 2", '/tmp/mpv-2', 27, 17, 22),
            RotaryEncoder("Rotary encoder 3", '/tmp/mpv-3', 26, 6, 16)
        ]

        while True:
            sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting gracefully.")
        GPIO.cleanup()
    except Exception as e:
        print(f"An error occurred: {e}")
        GPIO.cleanup()
