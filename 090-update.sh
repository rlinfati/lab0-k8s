#!/bin/sh

set -ex

kubectl get rs --all-namespaces --no-headers | awk '$4==0 {print $1, $2}' | while read ns rs; do
  kubectl delete rs -n $ns $rs
done

kubectl cordon $(hostname -f)
kubectl drain $(hostname -f) --delete-emptydir-data --ignore-daemonsets

sudo kubeadm upgrade plan
sudo kubeadm config images pull
sudo kubeadm upgrade apply v1.36.2
sudo kubeadm upgrade node

for i in $( sudo podman image ls -a --format '{{.Tag}} {{.ID}}' | grep v1.35.6 | cut -f2 -d\   ); do sudo podman image rm $i; done

kubectl uncordon $(hostname -f)

sudo podman image prune --force
sudo podman image ls -a | sort

# eof
