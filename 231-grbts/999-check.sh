#!/bin/sh

set -ex

kubectl -n grbts get secrets,configmap
kubectl -n grbts get serviceaccount
kubectl -n grbts get role,rolebinding
kubectl -n grbts get clusterrole,clusterrolebinding

kubectl -n grbts get all
kubectl -n grbts get sc,pv,pvc

kubectl -n grbts logs deployment/grbts

# eof
