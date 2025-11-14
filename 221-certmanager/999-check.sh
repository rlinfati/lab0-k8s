#!/bin/sh

set -ex

kubectl -n cert-manager get all
kubectl -n cert-manager get secrets,configmap

kubectl get certificaterequest,order,challenge,certificate -A

# eof
