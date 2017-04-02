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
python manage.py makemigrations
python manage.py migrate
```
## 4. Celebrate :beers: :beers:
