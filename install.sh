# NOTE: This script assumes the host OS is Ubuntu 22.04 running on an x86_64 machine (VM)
# ToDo: modify to detect OS (for those using Debian) to instal the appropriate version of
# wxPython

#update the system, and install python3, pip
echo 'Updating the package repos, and installing python3, pip, and libsdl2 for wxpython'
sudo apt update
sudo apt install -y python3 python3-pip python3-virtualenv libsdl2-2.0-0

#Install the other packages wheel.
echo 'Installing python packages.'
virtualenv .venv #create virtualenv
source .venv/bin/activate 
python3 -m pip install -r requirements.txt 
python3 -m pip install https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04/wxPython-4.2.0-cp310-cp310-linux_x86_64.whl

#add the current user to the dialout group
echo 'Adding '$USER' to the dialout group.'
sudo usermod -a -G dialout $USER
#logout of system and login
#or run every command with sudo
