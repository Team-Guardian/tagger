#!/bin/bash

# Target Analysis and Geolocation (TAG) tool setup script
# installs dependencies and sets up the environment

# collect dependencies
sudo apt-get -qq update
sudo apt-get install -y qttools5-dev-tools python-pyqt5 postgresql python-psycopg2 python-pip pgadmin3 python-pyexiv2 python-numpy python-gdal pyqt5-dev-tools python-pip pgadmin3 python-pyexiv2 python-numpy python-gdal pyqt5-dev-tools
sudo pip install django setuptools watchdog pytest

psswd=postgres
username=postgres
dbname=tagger

# when postgres is installed, passwd is blank
# change default postgres user psswd to 'postgres'
echo "Changing password for user '$username' to '$psswd'"
sudo su $username -c "psql -U $username -c \"alter user $username with password '$psswd';\""
sudo su $username -c "createdb -O $username $dbname"