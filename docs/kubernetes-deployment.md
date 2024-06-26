
```bash
# create a random password for the database
kubectl create secret generic postgres-password --type=string --from-literal=password=$(pwgen 42 1)

# create deployment (needs the password secret)
# this will be starting the data ingestion process which takes a while for the first time
kubectl apply -f kubernetes-deployment.yaml
```
