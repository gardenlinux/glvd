# Deploy GLVD in your own Kubernetes Cluster

The `glvd` application can be deployed to both development and production Kubernetes clusters. It is designed to work with any standard Kubernetes cluster that meets the necessary resource requirements. Testing has been performed on Gardener clusters, but other environments should also be compatible.

If you need to set up your own cluster for development or debugging, ensure that you select a machine type with at least 4 CPUs and 7 GB of memory. For example, the `c3.xlarge` instance type on AWS is suitable.

To deploy `glvd`, use the `deploy-k8s.sh` shell script. This script requires both `pwgen` and `kubectl` to be installed. Before running the script, verify that `kubectl` is configured to target the intended cluster.

Once deployed, you can access the application by configuring an ingress or by using `kubectl port-forward`.

Example to forward the port 8080 to the service:

```
kubectl -n glvd port-forward service/glvd 8080
```

Now, you can access your deployment via http://localhost:8080
