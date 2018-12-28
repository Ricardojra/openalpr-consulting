#!/usr/bin/bash
# Install alpr_image_scanner and configure to run as daemon

# Install OpenALPR SDK and Agent ---------------------------------------------
curl -L https://deb.openalpr.com/openalpr.gpg.key | sudo apt-key add -
echo 'deb https://deb.openalpr.com/bionic/ bionic main' | sudo tee /etc/apt/sources.list.d/openalpr.list
sudo apt-get update
sudo apt-get install -o apt::install-recommends=true -y openalpr libopenalpr-dev libalprstream-dev python3-openalpr openalpr-video
sudo apt-get install -o apt::install-recommends=true -y openalpr-daemon openalpr-link
sudo rm /etc/apt/sources.list.d/openalpr.list

# Confirm license key is present ---------------------------------------------
if [ ! -d "/etc/openalpr/license.conf" ]; then
    echo "Error: no license.conf file in /etc/openalpr" 1>&2
    exit 1
fi
 
# Install required Python3 packages ------------------------------------------
sudo apt-get install -y python3-pillow python3-opencv python3-requests

# Copy files to appropriate locations ----------------------------------------
sudo cp ./{alprstream.py,vehicleclassifier.py} /usr/lib/python3/dist-packages
sudo cp ./libalprstream.so.3 /usr/lib/
sudo cp ./{alpr_image_scanner,rdb_saveimage} /usr/bin
sudo cp ./alpr_image_scanner.service /lib/systemd/system

# Enable daemon service ------------------------------------------------------
sudo systemctl daemon-reload
sudo systemctl enable alpr_image_scanner.service
sudo systemctl start alpr_image_scanner.service
