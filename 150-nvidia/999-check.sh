#!/bin/sh

set -ex

kubectl -n kube-nvidia get secrets,configmap
kubectl -n kube-nvidia get serviceaccount
kubectl -n kube-nvidia get role,rolebinding
kubectl -n kube-nvidia get clusterrole,clusterrolebinding

kubectl -n kube-nvidia get all
kubectl -n kube-nvidia get sc,pv,pvc

kubectl -n kube-nvidia logs daemonset.apps/nvidia-device-plugin
kubectl describe node

kubectl -n kube-nvidia delete   pod -l name=nvidia-device-plugin
kubectl -n kube-nvidia describe pod -l name=nvidia-device-plugin

# eof
