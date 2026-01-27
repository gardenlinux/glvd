#!/bin/bash

# Script to start (unhibernate) the 'dev' cluster in the 'garden-gl-dev' namespace.
# The 'dev' cluster is configured with a hibernation schedule and must be manually started when needed.
# Ensure your kubeconfig is set to the correct Garden cluster context before running this script.

if kubectl get shoot dev -n garden-gl-dev &>/dev/null; then
  kubectl patch shoot -n garden-gl-dev dev -p '{"spec":{"hibernation":{"enabled": false}}}'
else
  echo "Shoot 'dev' does NOT exist in namespace garden-gl-dev."
  echo "Make sure to have the correct kubeconfig active"
fi
