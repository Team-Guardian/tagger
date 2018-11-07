#!/bin/bash

# Target Analysis and Geolocation (TAG) tool setup script
# installs dependencies and sets up the environment

MY_YESNO_PROMPT='>> (y/n)$ '

echo ">> This is a script to assist with installation of the Tagger by Team Guardian.";
echo ">> Would you like to continue and install all the dependencies of Tagger?";
echo -n "$MY_YESNO_PROMPT"
read confirm

if [ $confirm = "n" ] || [ $confirm = "N" ] || [ $confirm = "no" ] || [ $confirm = "No" ]
then
    exit 0
    break
fi

# create a log file to make terminal output less noisy
touch .install.log; > .install.log

# collect and install system dependencies
sudo apt-get update >> .install.log # make sure we have the up-to-date package list
sudo apt-get -y install qttools5-dev-tools pyqt5-dev-tools >> .install.log # install system packages for working with Qt5
sudo apt-get -y install exiv2 libgdal20 >> .install.log # install packages that will be wrapped with python
sudo apt-get -y install libexiv2-dev libgdal-dev libboost-all-dev >> .install.log # install headers for compiling packages
sudo apt-get -y install postgresql pgadmin3 >> .install.log # install PostgreSQL database and PgAdmin GUI to work with it
sudo apt-get -y install build-essential python-all-dev libboost-python-dev>> .install.log #install py3exiv2 prerequisites to build it locally
# collect and install python3 dependencies
sudo apt-get -y install python3-pip >> .install.log # install pip for python3 if not installed yet
python3 -m pip install --user pipenv >> .install.log # get dependencies manager pipenv, only install for current user

# temporarily modify path so bash knows where to find pipenv
# path will stay changed for the current bash session
# to change it back, close current terminal window and open the new one
echo ">> Modify PATH for the current session only to install dependencies for the current user only";
echo ">> PATH will be changed back when you close this terminal window and launch another one";

export PATH=$PATH:$HOME/.local/bin

sudo apt-get -y install python3-gdal >> .install.log # Known issue with GDAL so this is a patch

pipenv install # will list dependencies from the Pipfile

# pipenv install setuptools >> .install.log # need it to install some packages
# pipenv install requests psycopg2 py3exiv2 watchdog numpy PyQt5 django >> .install.log # install python3 packages
# pipenv install pygdal==2.2.1.3 >> .install.log

# [Not included for now, instead run `sudo apt-get install python3-gdal`]
# ==========================================================================================================================
# there's a bug with GDAL: https://gis.stackexchange.com/questions/28966/python-gdal-package-missing-header-file-when-installing-via-pip
# so that it can't find header files even though they are available
# point the compiler to the header files manually here and then install the python package
# export CPLUS_INCLUDE_PATH=/usr/include/gdal
# export C_INCLUDE_PATH=/usr/include/gdal

# pipenv install GDAL=2.2.3 >> .install.log
# ==========================================================================================================================

# psswd=postgres
# username=postgres
# dbname=tagger

# # when postgres is installed, passwd is blank 
# # change default postgres user psswd to 'postgres'
# echo "Changing password for user '$username' to '$psswd'"
# sudo su $username -c "psql -U $username -c \"alter user $username with password '$psswd';\""
# sudo su $username -c "createdb -O $username $dbname"
