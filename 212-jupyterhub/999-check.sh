#!/bin/sh

set -ex

kubectl -n jupyterhub get secrets,configmap
kubectl -n jupyterhub get serviceaccount
kubectl -n jupyterhub get role,rolebinding
kubectl -n jupyterhub get clusterrole,clusterrolebinding

kubectl -n jupyterhub get all
kubectl -n jupyterhub get sc,pv,pvc

kubectl -n jupyterhub logs deployment/jupyterhub

# eof
