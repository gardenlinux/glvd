#!/bin/bash

if ! [ -x "$(command -v pwgen)" ]; then
  echo 'Error: pwgen is not installed.' >&2
  exit 1
fi

if ! [ -x "$(command -v kubectl)" ]; then
  echo 'Error: kubectl is not installed.' >&2
  exit 1
fi

if kubectl get secret | grep -q postgres-credentials ; then
    DB_PASSWORD=$(kubectl get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)
    echo 'found existing db credentials, re-using'
else
    DB_PASSWORD=$(pwgen 42 1)
    kubectl create secret generic postgres-credentials --type=string --from-literal=username=glvd --from-literal=password="$DB_PASSWORD"
    echo 'did not find existing db credentials, creating new'
fi

if kubectl get secret | grep -q pgadmin-credentials ; then
    PGADMIN_PASSWORD=$(kubectl get secret/pgadmin-credentials --template="{{.data.password}}" | base64 -d)
    echo 'found existing pgadmin credentials, re-using'
else
    PGADMIN_PASSWORD=$(pwgen 42 1)
    kubectl create secret generic pgadmin-credentials --type=string --from-literal=password="$PGADMIN_PASSWORD"
    echo 'did not find existing pgadmin credentials, creating new'
fi

kubectl apply -f deployment/k8s/00_db-statefulset.yaml

echo 'waiting for db pod to become ready'
kubectl wait --for=condition=ready pod -l app=statefulset.kubernetes.io/pod-name=glvd-database-0 --timeout=120s

if kubectl get po | grep -q init-pg ; then
    echo 'init-pg container exists, skipping init for now'
else
    kubectl run init-pg --image=ghcr.io/gardenlinux/glvd-init:latest --restart=Never --env=PGHOST=glvd-database-0.glvd-database --env=PGPASSWORD="$DB_PASSWORD"
    echo 'give init some time to complete'
    sleep 60
fi

kubectl apply -f deployment/k8s/01_glvd-deployment.yaml
kubectl apply -f deployment/k8s/02_ingestion-job.yaml
