#!/bin/sh

set -ex

kubectl -n ingress-nginx get all
kubectl -n ingress-nginx get secrets,configmap

kubectl get ingress -A

# eof
