#!/bin/bash

export PGUSER=glvd
export PGDATABASE=glvd
export PGPASSWORD=glvd
export PGHOST=localhost
export PGPORT=5432
PYTHONPATH=src quart --app glvd.web run
