#!/bin/sh

set -ex

kubectl get rs --all-namespaces --no-headers | awk '$4==0 {print $1, $2}' | while read ns rs; do
  kubectl delete rs -n $ns $rs
done

kubectl cordon $(hostname -f)
kubectl drain $(hostname -f) --delete-emptydir-data --ignore-daemonsets

sudo kubeadm upgrade plan
sudo kubeadm config images pull
sudo kubeadm upgrade apply v1.34.3
sudo kubeadm upgrade node

kubectl uncordon $(hostname -f)

# eof
