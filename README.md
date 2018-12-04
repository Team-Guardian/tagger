Install Git package.
```
sudo apt-get install git
```
Clone Team-Guardian's Tagger repository.
```
git clone https://github.com/Team-Guardian/tagger.git
```
Change permission of the installation script.
```
chmod 755 install.sh
```
Run installation script for tagger
```
./install.sh
```
Enter tagger's isolated environment
```
sudo python3 -m pipenv shell
```
Setup the database (One line at a time)
```
sudo -i -u postgres
psql
\password
postgres
postgres
create database tagger with owner postgres;
\q
exit
sudo service postgresql restart
python manage.py makemigrations
python manage.py migrate
```
You are all done! Run the tagger program
```
python3 main.py
```


