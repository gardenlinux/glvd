#!/bin/bash

if kubectl get secret | grep -q postgres-credentials ; then
    DB_PASSWORD=$(kubectl get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)
    echo 'found existing db credentials, re-using'
else
    DB_PASSWORD=$(pwgen 42 1)
    kubectl create secret generic postgres-credentials --type=string --from-literal=username=glvd --from-literal=password="$DB_PASSWORD"
    echo 'did not find existing db credentials, creating new'
fi

kubectl apply -f 00_db-statefulset.yaml

echo 'give db some time to pull image and start'
sleep 30

if kubectl get po | grep -q init-pg ; then
    echo 'init-pg container exists, skipping init for now'
else
    kubectl run init-pg --image=ghcr.io/gardenlinux/glvd-postgres-init:latest --restart=Never --env=PGHOST=glvd-database-0.glvd-database --env=PGPASSWORD="$DB_PASSWORD"
    echo 'give init some time to complete'
    sleep 60
fi

kubectl apply -f 01_glvd-deployment.yaml
kubectl apply -f 02_ingestion-job.yaml