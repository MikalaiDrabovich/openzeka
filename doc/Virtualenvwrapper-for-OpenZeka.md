# Installation of Virtualenvwrapper

    sudo pip install virtualenvwrapper

Add three line to your `.bashrc` file

    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/Devel
    source /usr/local/bin/virtualenvwrapper.sh

Then source your `.bashrc` file

    source ~/.bashrc

Run:

    workon

A list of environments, empty, is printed.

Run:

    mkvirtualenv openzekaenv

A new environment, `openzekaenv` is created and activated.

Run:

    workon openzekaenv

## Install some dependencies

    sudo apt-get install python-cffi-backend
    sudo apt-get install libffi-dev

## Clone OpenZeka code repository

    git clone https://github.com/ferhatkurt/openzeka.git
    cd openzeka
    sudo pip install -r requirements.txt

## Download Reference CaffeNet Model and the ImageNet Auxiliary Data

    ./scripts/download_model_binary.py models/bvlc_reference_caffenet
    ./data/ilsvrc12/get_ilsvrc_aux.sh

## Now you can install NGINX

    chmod +x insall-nginx.sh
    ./install-nginx.sh

## Running Web and API Server

You are ready to run Web & API Server. [Click here to learn how to start servers](https://github.com/ferhatkurt/openzeka/wiki/Running-Web-and-API-Server)

**If you get an error about missing library please try to install pycaffe requirements.txt in your `openzekaenv`**