#!/bin/sh

set -ex

export K8SNS=kube-nvidia
export K8SNS=localpath
export K8SNS=jupyterhub
export K8SNS=cert-manager
export K8SNS=ingress-nginx
export K8SNS=grbts
export K8SNS=strongswan
export K8SNS=cloudflared

kubectl -n $K8SNS get secrets,configmap
kubectl -n $K8SNS get serviceaccount
kubectl -n $K8SNS get role,rolebinding
kubectl -n $K8SNS get clusterrole,clusterrolebinding
kubectl -n $K8SNS get certificaterequest,order,challenge,certificate
kubectl -n $K8SNS get ingress
kubectl -n $K8SNS get all
kubectl -n $K8SNS get sc,pv,pvc
kubectl describe node

kubectl -n kube-nvidia logs daemonset.apps/nvidia-device-plugin
kubectl -n kube-nvidia describe pod -l name=nvidia-device-plugin

kubectl -n localpath logs deployment/localpath

kubectl -n jupyterhub logs deployment/jupyterhub

kubectl -n cert-manager logs deployment/cert-manager-cainjector
kubectl -n cert-manager logs deployment/cert-manager-webhook
kubectl -n cert-manager logs deployment/cert-manager

kubectl -n ingress-nginx logs deployment/ingress-nginx-controller

kubectl -n grbts logs deployment/grbts

kubectl -n strongswan logs deployment/swan

kubectl -n cloudflared logs deployment/cloudflared

# eof
