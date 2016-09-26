#!/usr/bin/env bash
# After caffe install go pycaffe
# This script will install Pycaffe for Ubuntu 14.04, Ubuntu 16.04, Jetson TX1, and Jetson TK1
# How many cores you want to use during installation. Jetson has 4 cores.
NUM_CORES=4
# If you install caffe with install-caffe.sh file your caffe main directory should be HOME/caffe
# If you install caffe other directory please change below
CAFFE_HOME="$HOME/caffe"
#Additional
sudo apt-get install -y python-pip
sudo pip install scipy # required by scikit-image
sudo apt-get install -y python-scipy # in case pip failed

cd $CAFFE_HOME/python
for req in $(cat requirements.txt); do sudo pip install $req; done
echo "export PYTHONPATH=$(pwd):$PYTHONPATH " >> ~/.bashrc # to be able to call "import caffe" from Python after reboot
source ~/.bashrc # Update shell
sudo ldconfig
cd ..
make pycaffe -j$NUM_CORES