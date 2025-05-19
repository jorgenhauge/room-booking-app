A toy room booking system
=====
The web application is build with python Flask framwork along with SQLite3 database. It has basic login system since the booking have to be done with authentication. A admin account is created by default, with username: admin, and password: admin. The administrator have the access to directly manipulate team and users. 

## Optional
Install SQLite browser [Available](http://sqlitebrowser.org/)

## Installation
1. Install flask and packages
```bash
pip install .
```

## Setup
1. Define the project
```bash
export FLASK_APP="app:create_app"
export FLASK_ENV=development
```

2. Init the database
```bash
flask db init
```

## Migrating data
1. Run the migration command from the project directory to create tables
```bash
flask db upgrade
```
2. Populate the database with dummy data(if weren't populated after migration)
```bash
python populate.py
```

# Running
1. Run the flask application from the project directory, running on localhost
```bash
flask run
```
2. Open the app in browser: [localhost](http://127.0.0.1:5000/)
