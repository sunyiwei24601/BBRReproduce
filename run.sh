#!/bin/bash
apt-get update
apt-get install git
git clone https://github.com/sunyiwei24601/CopaReproduce.git
apt-get install python3-pip
pip3 install mininet

# install mininet tools
git clone https://github.com/mininet/mininet
mininet/util/install.sh -a

# download deb files
mkdir bbr_deb
cd bbr_deb
wget https://storage.googleapis.com/copareproduce/linux-image-4.14.91bbr-init4_4.14.91bbr-init4-2_amd64.deb -O bbr-init4.deb
wget https://storage.googleapis.com/copareproduce/linux-image-4.14.91bbr-150_4.14.91bbr-150-1_amd64.deb -O bbr-150.deb
wget https://storage.googleapis.com/copareproduce/linux-headers-4.14.91bbr-init4_4.14.91bbr-init4-2_amd64.deb -O bbr-init4-headers.deb
wget https://storage.googleapis.com/copareproduce/linux-headers-4.14.91bbr-150_4.14.91bbr-150-1_amd64.deb -O bbr-150-headers.deb
dpkg -i bbr-init4.deb
dpkg -i bbr-150.deb

#sudo vim /etc/default/grub.d/50-cloudimg-settings.cfg
#sudo update-grub