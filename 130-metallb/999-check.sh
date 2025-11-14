#!/bin/sh

set -ex

kubectl -n metallb-system get secrets,configmap
kubectl -n metallb-system get serviceaccount
kubectl -n metallb-system get role,rolebinding
kubectl -n metallb-system get clusterrole,clusterrolebinding

kubectl -n metallb-system get all
kubectl -n metallb-system get sc,pv,pvc

# eof
