# Enable I2C in raspi-config

# Set higher baudrate in /boot/firmware/config.txt for higher fps
# Find the line containing “dtparam=i2c_arm=on”.
# Add “,i2c_arm_baudrate=400000” where 400000 is the new speed (400 Kbit/s). Note the comma in the beginning.
# This should give you a line looking like:
# dtparam=i2c_arm=on,i2c_arm_baudrate=400000
# For comparision, default baudrate is only 100 KBit/s.

# Get your OLED display's device address using i2cdetect from i2c-tools package:
# i2cdetect -y 1
# Set its address below in the code.

# Set correct device driver for your OLED display
# in the code below depending on which driver IC your display has.

# Configure MPV socket paths in main function below.
# Run each MPV instance with --input-ipc-server=/path/to/socket
# Here: /tmp/mpv-1, /tmp-mpv-2 or /tmp/mpv-3 as configured below.

# Set path to suitable OTF or TTF font below and maybe adjust font size.

# Requires Python packages luma.oled pillow and several others.
# On the Raspberry Pi, create a virtual Python environment like this:
# python -m venv /path/to/mpv-control
# Activate virtual environment:
# source /path/to/mpv-control/bin/activate
# Install packages:
# pip install luma.oled pillow
# This collects all other needed packages and installs them.

# To run this script
# activate virtual Python environment:
# source /path/to/mpv-control/bin/activate
# Run script:
# python /path/to/mpv-oled-control.py
# Exit with CTRL-C

import threading
import socket
import json
import time
import os
import select
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont

# Load a font and set font size
font_size = 21
# TTF and OTF fonts are valid (for both 'ImageFont.truetype' is used.
font = ImageFont.truetype("/path/to/hvb_____.ttf", font_size)
#example: font = ImageFont.truetype("/home/USER/.local/share/fonts/hvb_____.ttf", font_size)

# Set your OLED display's device address here.
serial = i2c(port=1, address=0x3c)
# Set correct device driver for your OLED display
device = sh1106(serial)

# Set the contrast (values usually range from 0 to 255)
device.contrast(127)

state_lock = threading.Lock()

update_event = threading.Event()

# Global states of all MPV instances
mpv_states = {'1': {'volume': 0.0, 'mute': True, 'active': False},
              '2': {'volume': 0.0, 'mute': True, 'active': False},
              '3': {'volume': 0.0, 'mute': True, 'active': False}}

# Flag to control the running of threads
running = True

def socket_exists(socket_path):
    return os.path.exists(socket_path)

# Display all MPV instances' states
def update_display(device, states):
    global running
    while running:
        start_time = time.time()

        max_frame_rate = 30

        event_triggered = update_event.wait(timeout=1/max_frame_rate)  # Wait for an update event or timeout
        if event_triggered:
            with state_lock:
                with canvas(device) as draw:
                    line_height = font_size + 0
                    for idx, state in states.items():
                        if state['active']:
                            volume = state['volume']
                            mute_status = state['mute']
                            mute_indicator1 = "- " if mute_status else ""
                            mute_indicator2 = " -" if mute_status else ""
                            try:
                                volume_int = int(volume)
                                text = f"{idx}: {mute_indicator1}{volume_int}%{mute_indicator2}"
                            except ValueError:
                                text = f"{idx}: {mute_indicator1}???%{mute_indicator2}"
                        else:
                            text = f"{idx}: - Dead -"

                        draw.text((0, line_height * (int(idx) - 1)), text, fill="white", font=font)

            update_event.clear()  # Reset the event after handling

        elapsed_time = time.time() - start_time  # Time taken for the current loop
        sleep_time = max(1/max_frame_rate - elapsed_time, 0)  # Calculate remaining time to sleep
        time.sleep(sleep_time)  # Sleep to maintain a minimum of 1/max_frame_rate seconds per loop

# Handle MPV instances
def handle_mpv_instance(socket_path, instance_id):
    global mpv_states, running

    while running:
        if socket_exists(socket_path):
            mpv_states[str(instance_id)]['active'] = True
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(socket_path)
                print(f"Observation is active on: {socket_path}")

                # Observe volume and mute properties
                for prop in ["volume", "mute"]:
                    observe_command = json.dumps({"command": ["observe_property", 1, prop]})
                    sock.sendall(observe_command.encode('utf-8') + b'\n')

                buffer = ""
                while running:
                    # Using select for non-blocking socket reading with a timeout allowing periodic checking of running flag
                    ready = select.select([sock], [], [], 1)
                    if ready[0]:
                        data = sock.recv(1024).decode()
                        if not data:
                            break

                        buffer += data
                        while "\n" in buffer:
                            message, buffer = buffer.split("\n", 1)
                            try:
                                event = json.loads(message)
                                if 'event' in event and event['event'] == 'property-change':
                                    with state_lock:
                                        mpv_states[str(instance_id)][event['name']] = event.get('data', '-')
                                        update_event.set()  # Signal that an update is needed
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error in {socket_path}: {e}")
                                print(f"Faulty message: {message}")
                            except KeyError as e:
                                print(f"Key error: {e}")

            except ConnectionRefusedError:
                print(f"Connection refused for {socket_path}. MPV might not be running.")
                with state_lock:
                    mpv_states[str(instance_id)]['active'] = False
                    update_event.set()
                time.sleep(1)
            except Exception as e:
                print(f"Error in handle_mpv_instance for {socket_path}: {e}")
            finally:
                sock.close()

        else:
            mpv_states[str(instance_id)]['active'] = False
            update_event.set()
            print(f"Socket file {socket_path} does not exist. Waiting for MPV to start.")
            time.sleep(1)

        # Delay before the next check
        time.sleep(1)

def main():
    global running
    threads = []

    # Start display update thread
    display_thread = threading.Thread(target=update_display, args=(device, mpv_states))
    display_thread.start()
    threads.append(display_thread)

    # Initialize socket paths and start threads for handling MPV instances
    sockets = ['/tmp/mpv-1', '/tmp/mpv-2', '/tmp/mpv-3']
    for idx, socket_path in enumerate(sockets):
        thread = threading.Thread(target=handle_mpv_instance, args=(socket_path, idx+1))
        threads.append(thread)
        thread.start()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Caught CTRL-C, stopping threads...")
        running = False
        for thread in threads:
            thread.join()
        print("Threads stopped. Exiting gracefully.")

if __name__ == "__main__":
    main()
