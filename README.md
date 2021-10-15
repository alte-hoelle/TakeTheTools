
# TakeTheTools
A prototype for a digital equipment rental service for self-managed collectives, open workshops, shared warehouses and fablabs

An often encountered problem in open workshops such as ours, is that many people visit us and want to borrow tools, especially during events.
Handling that with sprawling excel sheets or even worse, paper was no longer an option. 
With this we aim to create a tool which enables us to electronically lend tools or equipment to users. 
This works by first making inventory of all our stuff and afterwards sticking the automatically generated barcodes to all tools. We can than register users
with 125 kHz RFID chips. They can than scan all the tools they want to borrow and enter an expected return date. Afterwards they can checkout their cart with either
their chip or a username/password combination.

## deployment

Clone the repo to a directory of your choice. Install [poetry](https://python-poetry.org/docs/) for installing dependencies.  
Copy ```src/takethetools/secrets_dev.py``` to ```src/takethetools/secrets_prod.py``` and insert random salts.  
Edit ```src/takethetools/settings.py``` and set ```ENVIRONMENT``` to ```prod``` and make sure the right IPs or Hostnames are set in ```ALLOWED_HOSTS```.  

Afterwards issue the following commands within the repo-directory: 

### the manual way

```bash
poetry install
poetry shell
cd src 
python manage.py makemigrations lendit
python manage.py migrate
python manage.py runserver 8080
```
The server should be reachable via [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

### docker

```bash
docker-compose build
docker-compose up -d
```
The server should be reachable via [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## development

### github actions local run

Install ```act``` by following the installation guide: https://github.com/nektos/act

run ```act``` in the project dir. That's all.

## Setup

If you want to start registering items, serveral steps have to be taken first. 
Make sure you add a location for the items first. Than register a Terminal User which is situated at the aforementioned Location. When creating Items, the location of the registering terminal User will be taken as the default item location.
Also, this may be changed, register one or multiple Owners for items you want to register in advance. This makes things easier in the process of adding items.

Consider adding multiple usage purposes, they help determing what things are used for and if you want to tell people to financially contribute to your workshop etc. We e.g. have "Private", "Commercial" and "association work" which result in differen multipliers for recommended donations.

## Interface
![leih](https://user-images.githubusercontent.com/1584749/111876908-10d3fb80-89a1-11eb-9ea3-ab28cf536c57.png)
![addtool](https://user-images.githubusercontent.com/1584749/111876911-129dbf00-89a1-11eb-98e0-adc3818c0dbb.png)
![tools](https://user-images.githubusercontent.com/1584749/111886671-cddd4c80-89cf-11eb-9e9f-072865ec1165.png)
