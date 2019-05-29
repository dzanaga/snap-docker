#!/bin/bash

# Get Miniconda and make it the main Python interpreter
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda.sh
bash /opt/miniconda.sh -b -p /opt/miniconda
rm /opt/miniconda.sh

# group add anaconda
# making conda available for all sudo users
chgrp -R sudo /opt/miniconda
chmod 770 -R /opt/miniconda

# "PATH=$PATH:/opt/miniconda/bin" >> .bashrc
