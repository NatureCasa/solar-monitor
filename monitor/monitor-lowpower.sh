#!/usr/bin/env bash
echo none | sudo tee /sys/class/leds/ACT/trigger
echo 1 | sudo tee /sys/class/leds/ACT/brightness
echo 0 | sudo tee /sys/class/leds/ACT/brightness
vcgencmd display_power 0 2
vcgencmd display_power 0 7
rfkill block wifi
echo "Low Power mode"
