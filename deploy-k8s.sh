#!/bin/bash

DB_PASSWORD=$(pwgen 42 1)

kubectl create secret generic postgres-credentials --type=string --from-literal=username=glvd --from-literal=password="$DB_PASSWORD"

kubectl apply -f 00_db-statefulset.yaml

sleep 20

kubectl run init-pg --image=ghcr.io/gardenlinux/glvd-postgres-init:latest --restart=Never --env=PGHOST=glvd-database-0.glvd-database --env=PGPASSWORD="$DB_PASSWORD"

sleep 60

kubectl apply -f 01_glvd-deployment.yaml
kubectl apply -f 02_ingestion-job.yaml
