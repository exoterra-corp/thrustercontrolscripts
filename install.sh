#update the system, and install python3, pip
echo 'Updating the package repos, and installing python3, pip, and libsdl2 for wxpython'
sudo apt update
sudo apt install -y python3 python3-pip libsdl2-2.0-0

#Install the other packages wheel.
echo 'Installing python packages.'
python3 -m pip install ./packages/canopen-1.2.4-py2.py3-none-any.whl
python3 -m pip install ./packages/python_can-4.0.11-py2.py3-none-any.whl
python3 -m pip install https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04/wxPython-4.1.1-cp38-cp38-linux_x86_64.whl
python3 -m pip install pyserial==3.5

#add the current user to the dialout group
echo 'Adding '$USER' to the dialout group.'
sudo usermod -a -G dialout $USER
#logout of system and login
#or run every command with sudo
