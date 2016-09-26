#!/usr/bin/env bash
# This script will install Caffe for Jetson TK1
# Some of the instructions taken from https://github.com/jetsonhacks/installCaffeJTX1

# How many cores you want to use during installation. Jetson has 4 cores.
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

# Additional libraries about possible errors about libffi and leveldb
sudo apt-get install python-cffi-backend
sudo apt-get install libffi-dev
sudo apt-get install python-leveldb

sudo usermod -a -G video $USER
/bin/echo -e "\e[1;32mCloning Caffe into the home directory\e[0m"
# Place caffe in the home directory
cd ~/
# Git clone Caffe
git clone https://github.com/BVLC/caffe.git
cd caffe

##Additional
#sudo apt-get install -y python-pip
#sudo pip install scipy # required by scikit-image
#sudo apt-get install -y python-scipy # in case pip failed

#cd python
#for req in $(cat requirements.txt); do sudo pip install $req; done
#echo "export PYTHONPATH=$(pwd):$PYTHONPATH " >> ~/.bashrc # to be able to call "import caffe" from Python after reboot
#source ~/.bashrc # Update shell
#sudo ldconfig
#cd ..

cp Makefile.config.example Makefile.config
# Enable cuDNN usage: Caffe is not support Jetson TK1 cudnn
# sudo sed -i 's/# USE_CUDNN := 1/USE_CUDNN := 1/' Makefile.config
# Enable with python layer
sudo sed -i 's/# WITH_PYTHON_LAYER := 1/WITH_PYTHON_LAYER := 1/' Makefile.config

mkdir build
cd build
cmake ..
cd ..

#make pycaffe -j$NUM_CORES
make all -j$NUM_CORES
# make test -j$NUM_CORES
make runtest -j$NUM_CORES
make distribute