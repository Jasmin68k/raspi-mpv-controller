#!/bin/bash

# Example script to end 3 MPV instances plus rotary encoder control and display of volume and mute states on an OLED display using screen sessions.

screen -S mpv-3 -X stuff $'Q'
screen -S mpv-2 -X stuff $'Q'
screen -S mpv-1 -X stuff $'Q'
screen -S mpv-rotary -X stuff $'\003'
screen -S mpv-oled -X stuff $'\003'
