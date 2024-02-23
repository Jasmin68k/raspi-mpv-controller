# Raspberry Pi MPV Controller

## Overview
This project integrates a Raspberry Pi with multiple rotary encoders and an I2C OLED display to control and monitor the state of several MPV media player instances.

It's an ideal setup for users looking to manage media playback in a convenient and interactive way.

## Features
- **Rotary Encoders**: Utilize rotary encoders for intuitive control of the MPV instances.
- **OLED Display**: Real-time display of the current state of each MPV instance.
- **Volume and Mute Control**: Currently configured to control and display the volume and mute states of the MPV instances.

## Configuration and Usage
All configuration details and usage instructions are contained within the scripts themselves.

This provides a straightforward way to get the system up and running, as well as to make any necessary adjustments.

## Customization
While the current setup is focused on controlling and displaying volume and mute states, the system is versatile.

Users can adapt it to control and display other MPV properties as needed.

## Installation
Please refer to the individual scripts for detailed installation and configuration instructions.

## Hardware Requirements
- **Raspberry Pi**: A Raspberry Pi model with GPIO pins
- **Rotary Encoders**: Rotary encoders with push-button functionality
- **I2C OLED Display**: A compatible I2C OLED display
- **Connecting Materials**: Jumper wires or your preferred method of connecting components to the Raspberry Pi GPIO pins.
- **Audio HAT or USB DAC (Strongly Recommended)**: The Raspberry Pi's onboard audio, if present, has significant quality limitations. An external audio solution (HAT or USB DAC) will provide a vastly superior audio experience for your media playback.

## Software Requirements
- **Raspberry Pi OS**: The latest version of Raspberry Pi OS (formerly known as Raspbian) is recommended.
- **MPV Media Player**: The MPV media player installed on your Raspberry Pi.
- **Python 3.x**: Python 3 and its package manager, pip.
- **Additional Python Packages and the Python library for your OLED display**: See scripts for details.
- **Pipewire (Highly Recommended)**: Install Pipewire to seamlessly manage playback of multiple audio streams. The default ALSA system is not suitable for this, and ALSA/dmix software mixing can lead to audio issues like crackling during extended playback.
