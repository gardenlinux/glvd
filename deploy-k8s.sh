#!/bin/bash

if ! [ -x "$(command -v pwgen)" ]; then
  echo 'Error: pwgen is not installed.' >&2
  exit 1
fi

if ! [ -x "$(command -v kubectl)" ]; then
  echo 'Error: kubectl is not installed.' >&2
  exit 1
fi

if kubectl --namespace glvd get secret | grep -q postgres-credentials ; then
    DB_PASSWORD=$(kubectl --namespace glvd get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)
    echo 'found existing db credentials, re-using'
else
    DB_PASSWORD=$(pwgen 42 1)
    kubectl --namespace glvd create secret generic postgres-credentials --type=string --from-literal=username=glvd --from-literal=password="$DB_PASSWORD"
    echo 'did not find existing db credentials, creating new'
fi

if kubectl --namespace glvd get secret | grep -q pgadmin-credentials ; then
    PGADMIN_PASSWORD=$(kubectl --namespace glvd get secret/pgadmin-credentials --template="{{.data.password}}" | base64 -d)
    echo 'found existing pgadmin credentials, re-using'
else
    PGADMIN_PASSWORD=$(pwgen 42 1)
    kubectl --namespace glvd create secret generic pgadmin-credentials --type=string --from-literal=password="$PGADMIN_PASSWORD"
    echo 'did not find existing pgadmin credentials, creating new'
fi

kubectl --namespace glvd apply -f deployment/k8s/00_db-statefulset.yaml

echo 'give db some time to pull image and start'
sleep 30

if kubectl --namespace glvd get po | grep -q init-pg ; then
    echo 'init-pg container exists, skipping init for now'
else
    kubectl --namespace glvd run init-pg --image=ghcr.io/gardenlinux/glvd-init:2025.11.21 --restart=Never --env=PGHOST=glvd-database-0.glvd-database --env=PGPASSWORD="$DB_PASSWORD"
    echo 'give init some time to complete'
    sleep 60
fi

kubectl --namespace glvd apply -f deployment/k8s/01_glvd-deployment.yaml
kubectl --namespace glvd apply -f deployment/k8s/02_ingestion-job.yaml
