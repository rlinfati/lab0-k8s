#!/bin/sh

set -ex

sudo kubeadm config images pull
sudo kubeadm init --config NoSwap.yaml

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl taint nodes $(hostname --long) node-role.kubernetes.io/control-plane:NoSchedule-
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
kubectl get cm -n kube-system kubeadm-config -o yaml | grep Subnet

sudo firewall-cmd --permanent --zone=public --add-service=http --add-service=https
sudo firewall-cmd             --zone=public --add-service=http --add-service=https
sudo firewall-cmd --zone=public --list-all

sudo firewall-cmd --permanent --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd --permanent --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd             --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd             --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd --zone=trusted --list-all

kubectl get all -A

# eof
