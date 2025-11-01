#!/bin/sh

set -ex

kubectl -n strongswan get secrets,configmap
kubectl -n strongswan get serviceaccount
kubectl -n strongswan get role,rolebinding
kubectl -n strongswan get clusterrole,clusterrolebinding

kubectl -n strongswan get all
kubectl -n strongswan get sc,pv,pvc

kubectl -n strongswan logs deployment/swan

# eof
