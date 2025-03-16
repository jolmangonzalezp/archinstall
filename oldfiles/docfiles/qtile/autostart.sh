#!/bin/sh

# Configure screen resolution
xrandr --output eDP1 --primary --mode 1366x768 --pos 0x0 --rotate normal --output DP1 --off --output DP2 --off --output DP3 --off --output DP4 --off --output HDMI1 --off --output VIRTUAL1 --off

# Run compositer
picom &

# Run polkit auth
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 & eval $(gnome-keyring-daemon -s --components=pkcs11,secrets,ssh,gpg)

# Systray
udiskie -t &
nm-applet &
# volumeicon &
# cbatticon -u 5 &
blueman-applet &

# Setting wallpaper
nitrogen --restore &