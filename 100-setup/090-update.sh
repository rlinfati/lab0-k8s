#!/bin/sh

set -ex

kubectl cordon $(hostname -f)
kubectl drain $(hostname -f) --delete-emptydir-data --ignore-daemonsets

curl https://download.opensuse.org/repositories/isv:/cri-o:/stable:/v1.34/rpm/isv:cri-o:stable:v1.34.repo                      | sudo tee /etc/yum.repos.d/cri-o.repo
curl https://download.opensuse.org/repositories/isv:/kubernetes:/core:/stable:/v1.34/rpm/isv:kubernetes:core:stable:v1.34.repo | sudo tee /etc/yum.repos.d/kubernetes.repo
sudo dnf --exclude=kernel* --exclude=python3-perf --exclude=perf --exclude=bpftool --exclude=nvidia* --exclude=cuda* upgrade

sudo kubeadm upgrade plan
sudo kubeadm config images pull
sudo kubeadm upgrade apply v1.34.1
sudo kubeadm upgrade node

kubectl uncordon $(hostname -f)

# eof
