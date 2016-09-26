# Installing OpenZeka for Jetson TK1
Installation has 4 step. OpenZeka uses Caffe and pycaffe(with caffe/python/requirements.txt intallation). If you already installed them. Go third step and install OpenZeka then NGINX.

##1. Caffe installation
    sudo apt-get install curl
    git clone https://github.com/ferhatkurt/openzeka.git
    cd openzeka
    chmod +x insall-caffe-jetson-tk1.sh
    ./insall-caffe-jetson-tk1.sh

##2. Pycaffe installation
    chmod +x install-pycaffe.sh
    ./install-pycaffe.sh

##3. OpenZeka install
    chmod +x insall-openzeka.sh
    ./install-openzeka.sh

##4. NGINX install
    chmod +x insall-nginx.sh
    ./install-nginx.sh
##5. Running Web & API Server
**Close Terminal Window and Open A New One - It is important for the python caffe.**

You are ready to run Web and API Server. [Click here to learn how to start servers](https://github.com/ferhatkurt/openzeka/wiki/Running-Web-and-API-Server)