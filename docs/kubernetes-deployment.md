# GLVD Kubernetes deployment

This deployment guide is work in progress.
It is intended for development purposes so stakeholders can get a running version of the current development version of GLVD.

Assuming you have a Kubernetes cluster with enough resources (8 cpu, 16 GiB memory), that ideally should be located in the US, the following should give you a running cluster:

```bash
# create a random password for the database
kubectl create secret generic postgres-password --type=string --from-literal=password=$(pwgen 42 1)

# create persistent volume claim for postgres storage
kubectl apply -f 00-glvd-pvc.yaml

# create deployment (needs the password secret)
# this will be starting the data ingestion process which takes a while for the first time
kubectl apply -f 01-glvd-deployment.yaml

# create service to expose the api http interface
kubectl apply -f 02-glvd-service.yaml

# check the progress, the last line should say 'done'
kubectl logs -c data-ingestion glvd-SOME-ID

# get hostname of external service (this assumes only one hostname exists)
HOSTNAME=$(kubectl get svc glvd -o template --template '{{range .status.loadBalancer.ingress}}{{.hostname}}{{end}}')

# check for readiness
curl http://$HOSTNAME:8080/readiness

# use the API as described here https://gardenlinux.github.io/glvd-api/
# but use the HOSTNAME variable instead of glvd.gardenlinux.io for now
curl http://$HOSTNAME:8080/v1/cves/debian_linux/bookworm
```
