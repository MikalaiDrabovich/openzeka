#!/usr/bin/env bash

# Open Zeka Requirements
/bin/echo -e "\e[1;32mInstalling Open Zeka Dependencies.\e[0m"
sudo apt-get install python-cffi-backend
sudo apt-get install libffi-dev

sudo pip install -r requirements.txt

# Reference CaffeNet Model and the ImageNet Auxiliary Data
/bin/echo -e "\e[1;32mInstalling Open Zeka Reference CaffeNet Model and the ImageNet Auxiliary Data.\e[0m"
./scripts/download_model_binary.py models/bvlc_reference_caffenet
./data/ilsvrc12/get_ilsvrc_aux.sh
#Reference CaffeNet Model and the ImageNet Auxiliary Data