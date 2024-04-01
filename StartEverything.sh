#!/bin/bash

# Example script to start 3 MPV instances plus rotary encoder control and display of volume and mute states on an OLED display using screen sessions.
# List active screen sessions:
# screen -ls
# Attach to a running screen session:
# screen -r SESSIONNAME
# Example:
# screen -r mpv-1
# Detach from a running screen session:
# CTRL-A, CTRL-D

# You can adapt the socket names after the --input-ipc-server command, if you like.

# bash exits immediately, when program in screen session ends, so the screen sessions closes itself automatically. If that is not wanted, add "; exec bash" at the end.
# You can then exit the screen session with 'exit'.
screen -dmS mpv-oled bash -c "source /path/to/mpv-control/bin/activate ; python /path/to/mpv-oled-control.py"
screen -dmS mpv-rotary bash -c "source /path/to/mpv-control2/bin/activate ; python /path/to/mpv-rotary-control.py"
screen -dmS mpv-1 bash -c "mpv --input-ipc-server=/tmp/mpv-1 --script-opts=volumeid=YOURID1 --volume=$(cat /path/to/mpv_volume_YOURID1.txt) --mute=$(cat /path/to/mpv_mute_YOURID1.txt) /path/to/mediafile"
screen -dmS mpv-2 bash -c "mpv --input-ipc-server=/tmp/mpv-2 --script-opts=volumeid=YOURID2 --volume=$(cat /path/to/mpv_volume_YOURID2.txt) --mute=$(cat /path/to/mpv_mute_YOURID2.txt) /path/to/mediafile"
screen -dmS mpv-3 bash -c "mpv --input-ipc-server=/tmp/mpv-3 --script-opts=volumeid=YOURID3 --volume=$(cat /path/to/mpv_volume_YOURID3.txt) --mute=$(cat /path/to/mpv_mute_YOURID3.txt) /path/to/mediafile"

# Setup MPV with profiles in ~/.config/mpv/mpv.conf or additional command line parameters as you please.
# For live streams --loop-playlist=force is helpful, if you want MPV to reconnect and resume playback, when there is a network disturbance or when the stream ends and restarts right away or later.
# For live video streaming https://github.com/yt-dlp/yt-dlp can be used with MPV.
