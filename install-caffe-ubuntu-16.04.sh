#!/usr/bin/env bash
# This script will install Caffe for Ubuntu 16.04
# Some of the instructions taken from https://github.com/jetsonhacks/installCaffeJTX1

# How many cores you want to use during installation. Change in order to your core numbers.
NUM_CORES=4

sudo add-apt-repository universe
sudo apt-get update -y

# Install git
sudo apt-get install -y git

/bin/echo -e "\e[1;32mLoading Caffe Dependencies.\e[0m"
sudo apt-get install cmake -y
# General Dependencies
sudo apt-get install libprotobuf-dev libleveldb-dev libsnappy-dev \
libhdf5-serial-dev protobuf-compiler -y
sudo apt-get install --no-install-recommends libboost-all-dev -y
# BLAS
sudo apt-get install libatlas-base-dev -y
# Remaining Dependencies
sudo apt-get install libgflags-dev libgoogle-glog-dev liblmdb-dev -y

# added for numpy support
#sudo pip install numpy
sudo apt-get install -y python-numpy

#because of hdf5 error
sudo apt-get install -y python-h5py
sudo apt-get install -y python-cffi-backend
sudo apt-get install -y libffi-dev
sudo apt-get install -y python-leveldb

# (OpenCV 2.4)
sudo apt-get install -y libopencv-dev

sudo usermod -a -G video $USER
/bin/echo -e "\e[1;32mCloning Caffe into the home directory\e[0m"
# Place caffe in the home directory
cd ~/
# Git clone Caffe
git clone https://github.com/BVLC/caffe.git
cd caffe

cp Makefile.config.example Makefile.config
# Enable cuDNN usage
sudo sed -i 's/# USE_CUDNN := 1/USE_CUDNN := 1/' Makefile.config

# Enable with python layer
sudo sed -i 's/# WITH_PYTHON_LAYER := 1/WITH_PYTHON_LAYER := 1/' Makefile.config

# Add hdf5 library path and dir
echo "INCLUDE_DIRS += /usr/include/hdf5/serial" >> Makefile.config
echo "LIBRARY_DIRS += /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu/hdf5/serial" >> Makefile.config

mkdir build
cd build
cmake ..
cd ..

#make pycaffe -j$NUM_CORES
make all -j$NUM_CORES
make test -j$NUM_CORES
make runtest -j$NUM_CORES
make distribute
