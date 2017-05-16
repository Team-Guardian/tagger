# How to Get This Package Working

## 1. Installing All Dependencies
```
sudo apt-get update
sudo apt-get install qttools5-dev-tools python-pyqt5 postgresql python-psycopg2  python-pip pgadmin3 python-pyexiv2 python-numpy python-gdal pyqt5-dev-tools
sudo -H pip install django
sudo -H pip install setuptools
sudo -H pip install watchdog
```
## 2. PostgreSQL Installation and Setup

1. Open Terminal


2. Log in as user postgres
```
sudo -i -u postgres
```
3. Run the postgreSQL terminal interface
```
psql
```
4. Change password of currently postgres user to *postgres*
```
\password
postgres
postgres
```
5. Create a new database called *tagger* and set owner to *postgres* user.
```
create database tagger with owner postgres;
\q
```
6. Log out
```
exit
```
7. Restart postgreSQL service
```
sudo service postgresql restart
```
## 3. Creating Database Schema

In in the root of the project folder **tagger**
```
python manage.py migrate
```
## 4. Celebrate :beers: :beers:

# How to Set Up a Slave Tagger on a Local Area Network

## 1. Install dependencies
```
sudo apt-get update
sudo apt-get install sshfs openssh-server
```

## 2. Configure user groups
```
sudo groupadd fuse
sudo adduser <my_user> fuse
```

## 3. Create a destination directory for mapping in your tagger repo root directory
```
mkdir <path_to_tagger_repo>/remote_flights
```

## 4. Map GCS flights directory to the local folder you just created
```
sshfs uav@gcs-vision.local:/home/uav/tagger/flights <path_to_tagger_repo>/remote_flights
```

