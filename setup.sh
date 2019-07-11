#!/bin/sh

# used to gather all the add ons required for AudioElevator.py

#REUSABLE VARIABLES
YEL='\033[1;33m' #YELLOW HIGHLIGHT
NC='\033[0m' #NO COLOUR

echo "${YEL}Updating and Upgrading the system Prior to Installs${NC}"
sudo apt-get update
sudo apt-get upgrade

echo "${YEL}Making sure the system Time is up to date${NC}"
sudo apt-get install htpdate

echo "${YEL}Current Date${NC}"
date

echo "${YEL}Installing RPI.GPIO${NC}"
sudo pip3 install RPI.GPIO

echo "${YEL}Installing PyAudio${NC}"
sudo apt-get install python-pyaudio
sudo apt-get install git
sudo git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
sudo apt-get install python3-dev
cd pyaudio
sudo python3 setup.py install

echo "${YEL}Installing MAX9744 Amplifier Addons${NC}"
sudo pip3 install adafruit-circuitpython-max9744

echo "${YEL}Preparing i2c Setup for Run From Boot${NC}"
sudo sed -i 's/#dtparam=i2s=on/\dtparam=i2s=on/g' /boot/config.txt

echo "${YEL}Adding to the /etc/modules file for the SND interface.${NC}"
sudo echo "snd-bcm2835" >> /etc/modules

echo "${YEL}Gathering RPI-UPDATE${NC}"
sudo apt-get update
sudo apt-get install rpi-update
sudo rpi-update

echo "${YEL}Installing a series of required Devices${NC}"
sudo apt-get install git bc libncurses5-dev bison flex libssl-dev screen
sudo pip3 install sh

echo "${YEL}Downloading and installing required Kernel Source${NC}"
sudo wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /usr/bin/rpi-source
sudo chmod 755 /usr/bin/rpi-source
/usr/bin/rpi-source -q --tag-update
rpi-source --skip-gcc

echo "${YEL}Mounting and Preparing the Kernel${NC}"
sudo mount -t debugfs debugs /sys/kernel/debug

echo "${YEL}Download the required Module${NC}"
sudo git clone https://github.com/PaulCreaser/rpi-i2s-audio
cd rpi-i2s-audio

echo "${YEL}Making required my_loader${NC}"
sudo make -C /lib/modules/$(uname -r )/build M=$(pwd) modules
sudo insmod my_loader.ko

echo "${YEL}Verifying the module loaded${NC}"
sudo lsmod | grep my_loader
sudo dmesg | tail

echo "${YEL}Prepare my_loader for Autoload on Boot${NC}"
sudo cp my_loader.ko /lib/modules/$(uname -r)
echo 'my_loader' | sudo tee --append /etc/modules > /dev/null
sudo depmod -a
sudo modprobe my_loader

echo "${YEL}Prepare /etc/asound.conf for Default input/output${NC}"
sudo touch /etc/asound.conf
echo "pcm.!default{" >> /etc/asound.conf
echo "	type hw card 0" >> /etc/asound.conf
echo "}" >> /etc/asound.conf
echo "ctl.!default{" >> /etc/asound.conf
echo "	type hw card 0" >> /etc/asound.conf
echo "}" >> /etc/asound.conf

echo "${YEL}Creating a single boot file for Autostart${NC}"
sudo mv /home/pi/Desktop/AudioProject/audioElevate.py /home/pi/Desktop
sudo mv /home/pi/Desktop/AudioProject/forceStart.py /home/pi/Desktop

echo "${YEL}Preparing Autoboot Sequence${NC}"
echo "@lxterminal -e sudo python3 /home/pi/Desktop/forceStart.py" >> /etc/xdg/lxsession/LXDE-pi/autostart

echo "${YEL}Preparing config.desktop File${NC}"
sudo touch /home/pi/Desktop/config.desktop
sudo echo "[Desktop Entry]" >> /home/pi/Desktop/config.desktop
sudo echo "Name=config" >> /home/pi/Desktop/config.desktop
sudo echo "Comment=Link to config file" >> /home/pi/Desktop/config.desktop
sudo echo "Exec=lxterminal -e sudo leafpad /config.txt" >> /home/pi/Desktop/config.desktop
sudo echo "Type=Application" >> /home/pi/Desktop/config.desktop
sudo echo "Encoding=UTF-8" >> /home/pi/Desktop/config.desktop
sudo echo "Terminal=false" >> /home/pi/Desktop/config.desktop
sudo echo "Categories=None" >> /home/pi/Desktop/config.desktop
sleep 5

echo "${YEL}Preparing startMonitor.desktop File${NC}"
sudo touch /home/pi/Desktop/startMonitor.desktop
sudo echo "[Desktop Entry]" >> /home/pi/Desktop/startMonitor.desktop
sudo echo "Name=Start audioElevate" >> /home/pi/Desktop/startMonitor.desktop
sudo echo "Comment=Link to start python program" >> /home/pi/Desktop/startMonitor.desktop
sudo echo "Exec=lxterminal -e sudo python3 /home/pi/Desktop/forceStart.py" >> /home/pi/Desktop/startMonitor.desktop
sudo echo "Type=Application" >> /home/pi/Desktop/startMonitor.desktop
sudo echo "Encoding=UTF-8" >> /home/pi/Desktop/startMonitor.desktop
sudo echo "Terminal=true" >> /home/pi/Desktop/startMonitor.desktop
sudo echo "Categories=None" >> /home/pi/Desktop/startMonitor.desktop
sleep 5

echo "${YEL}Moving the CONFIG.TXT file to the Root Directory${NC}"
sudo mv /home/pi/Desktop/AudioProject/config.txt /

echo "${YEL}REBOOTING THE SYSTEM${NC}"
sudo reboot
