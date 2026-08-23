#!/bin/sh

set -ex

kubectl get rs --all-namespaces --no-headers | awk '$4==0 {print $1, $2}' | while read ns rs; do
  kubectl delete rs -n $ns $rs
done
kubectl delete job --all --all-namespaces

kubectl cordon $(hostname --long)
kubectl drain $(hostname --long) --delete-emptydir-data --ignore-daemonsets
kubectl get all --all-namespaces

sudo kubeadm upgrade plan
sudo kubeadm config images pull
sudo kubeadm upgrade apply v1.36.4
sudo kubeadm upgrade node

kubectl uncordon $(hostname --long)

# eof
