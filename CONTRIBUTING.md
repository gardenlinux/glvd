# Contributing

## Running tests

### Preparing PostgreSQL database

Running the tests requires a working PostgreSQL database.
It can be installed following the [PostgreSQL documentation](https://www.postgresql.org/download/linux/) on almost everything.
The database needs to accessible using the default means, so `psql` should work without extra config.

This should work on current Debian:
```
sudo apt install postgresql-16
sudo -u postgres psql -c "CREATE USER ${USER}; CREATE DATABASE ${USER} OWNER ${USER};"
```

## Preparing dependencies

Dependencies can be installed using `poetry install` into a private virtual environment.
Those can then be used by calling `poetry shell`.

Otherwise install them into the main system.
This requires Debian experimental for now.

```
sudo apt satisfy 'flake8, mypy, python3-asyncpg, python3-quart, python3-requests, python3-sqlalchemy (>= 2), python3-pytest, python3-pytest-asyncio, python3-requests-mock'
```

## Run tests

```
PYTHONPATH=src pytest
flake8
mypy .
```

## Run web interface

```
PYTHONPATH=src quart --app glvd.web run
```
