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
sudo apt-get install python-h5py
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
# Enable cuDNN usage
sudo sed -i 's/# USE_CUDNN := 1/USE_CUDNN := 1/' Makefile.config

# nvcaffe fp16 branch
# Enable FP16:
# Details: https://github.com/dusty-nv/jetson-inference/blob/master/docs/building-nvcaffe.md
#sudo sed -i 's/# NATIVE_FP16/NATIVE_FP16/g' Makefile.config

# Enable compute_53/sm_53: (enable FP16)
#sudo sed -i 's/-gencode arch=compute_50,code=compute_50/-gencode arch=compute_53,code=sm_53 -gencode arch=compute_53,code=compute_53/g' Makefile.config

# Enable with python layer
sudo sed -i 's/# WITH_PYTHON_LAYER := 1/WITH_PYTHON_LAYER := 1/' Makefile.config

# Add hdf5 library path and dir
echo "INCLUDE_DIRS += /usr/include/hdf5/serial" >> Makefile.config
echo "LIBRARY_DIRS += /usr/lib/aarch64-linux-gnu/hdf5/serial" >> Makefile.config

mkdir build
cd build
cmake ..
cd ..

#make pycaffe -j$NUM_CORES
make all -j$NUM_CORES
# make test -j$NUM_CORES
make runtest -j$NUM_CORES
make distribute