# BlueSock

A simple file sharing webapp that was not that simple to create.

## View website live.

[bluesock.herokuapp.com](http://bluesock.herokuapp.com)

# Installation

## Clone the repository.

```
$ git clone https://github.com/sajal-chuttani/BlueSock.git

$ cd BlueSock/
```

## Install PostgreSQL according to the official documentation.

[Official PostgreSQL Documentation](https://www.postgresql.org/download/)


## Create a database.

```
$ psql

# CREATE DATABASE <database_name>

# \q
```

## Create a .env file. Add the following environmental variables:

```
$ vim .env

FLASK_APP=main.py
FLASK_ENV=development
DATABASE_URI='postgres://<username>:<password>@<hostname>:<port>/<database_name>'
DATABASE='<database_name>'
```

## Create and activate a virtual environment.

```
$ python3 -m venv venv

$ source venv/bin/activate
```

## Install the requirements.

```
$ pip3 install -r requirements.txt
```

## Run the application.

```
$ flask run
```

## Browse to http://127.0.0.1 port 5000

[http://127.0.0.1:5000](http://127.0.0.1:5000)

# License

[MIT](https://opensource.org/licenses/MIT)
