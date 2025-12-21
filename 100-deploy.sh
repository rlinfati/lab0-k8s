#!/bin/sh

set -ex

URLREPO=https://raw.githubusercontent.com/rlinfati/lab0-k8s/refs/heads/master

# kubectl apply -f $URLREPO/namespace.yaml

# rm a && vi a && kubectl apply -f a
# rm a && vi a && kubectl delete -f a && kubectl apply -f a
# rm a && vi a && kubectl delete -f a && kubectl apply -f a && kubectl delete -f z && kubectl apply -f z

kubectl -n jupyterhub delete pod --all
kubectl -n grbts delete pod --all
kubectl -n strongswan delete pod --all
kubectl -n cloudflared delete pod --all
kubectl -n tailscale delete pod --all

sudo podman image prune --force
sudo podman image ls -a | sort


# eof
