# How to Get This Package Working

## 1. Install Git package.
```
sudo apt-get install git
```
## 2. Clone Team-Guardian's Tagger repository.
```
git clone https://github.com/Team-Guardian/tagger.git
```
## 3. Change permission of the installation script.
```
chmod 755 install.sh
```
## 4. Run installation script for tagger.
```
./install.sh
```
## 5. Enter tagger's isolated environment.
```
sudo python3 -m pipenv shell
```
## 6. PostgreSQL Installation and Setup

### 6.1. Open Terminal


### 6.2. Log in as user postgres
```
sudo -i -u postgres
```
### 6.3. Run the postgreSQL terminal interface
```
psql
```
### 6.4. Change password of currently postgres user to *postgres*
```
\password
postgres
postgres
```
### 6.5. Create a new database called *tagger* and set owner to *postgres* user.
```
create database tagger with owner postgres;
\q
```
### 6.6. Log out
```
exit
```
### 6.7. Restart postgreSQL service
```
sudo service postgresql restart
```
## 7. You are all done! Run the tagger program.
```
python3 main.py
```
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
