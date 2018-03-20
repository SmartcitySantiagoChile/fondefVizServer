#!/bin/bash
# Install Pip and update
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi
sudo apt -y install python-pip
sudo -H pip install --upgrade pip
sudo -H pip install -r requirements.txt
