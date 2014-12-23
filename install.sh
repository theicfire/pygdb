sudo apt-get update --fix-missing   
sudo apt-get install -y nasm build-essential python-dev libdwarf-dev libelf-dev
   
cd ~
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip install -U cython   
sudo pip install -U pytest

