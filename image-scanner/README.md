# Image Scanner

Completed for Andy Rubin on 12/28/2018  
Watches a folder for images, detects plates using AlprStream Python binding, inserts images into rollingDB, and uploads JSON to webserver.

# Prerequisites 

* OpenALPR commercial license
* Ubuntu 18.04 LTS
* Python3
* systemd installed and machine booted with systemd as init

# Installation

1. (Optional) Edit `alpr_image_scanner.service` at the `ExecStart` line if you would like to change the default folder to watch and webserver for upload. These are the `-d` and `-w` flags with defaults `/var/lib/openalpr/watch` and `https://cloud.openalpr.com`, respectively.
2. Open terminal, navigate to the folder with this README, and run `bash install.sh`
3. You can check the log file in `/var/log/alpr_image_scanner.log` for details on the status of the daemon.

