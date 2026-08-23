#!/bin/sh

set -ex

kubectl -n rbackup        rollout restart daemonset.apps/pp-rbackup
kubectl -n cloudflared    rollout restart daemonset.apps/pp-cloudflared
kubectl -n tailscale      rollout restart daemonset.apps/pp-tailscale
kubectl -n rbackup        delete pod -l app=rbackup-localpath
kubectl -n rbackup        delete pod -l app=rbackup-rec4cam
kubectl -n cloudflared    delete pod -l pod=cloudflared
kubectl -n tailscale      delete pod -l pod=tailscale

kubectl -n grbts          rollout restart daemonset.apps/pp-grbts
kubectl -n vlmcsd         rollout restart daemonset.apps/pp-vlmcsd
kubectl -n strongswan     rollout restart daemonset.apps/pp-strongswan
kubectl -n grbts          delete pod -l app=grbts
kubectl -n vlmcsd         delete pod -l app=vlmcsd
kubectl -n strongswan     delete pod -l app=swan

kubectl -n jupyterhub     rollout restart daemonset.apps/pp-lab0-hub
kubectl -n jupyterhub     rollout restart daemonset.apps/pp-lab0
kubectl -n jupyterhub     rollout restart daemonset.apps/pp-dockerstacks
kubectl -n jupyterhub     rollout restart daemonset.apps/pp-lab0-cuda
kubectl -n jupyterhub     delete pod -l app=jhub

sudo crictl images
sudo crictl images | grep "<none>"
sudo crictl images | awk '$2 == "<none>" {print $3}' | xargs -r sudo crictl rmi

# eof

