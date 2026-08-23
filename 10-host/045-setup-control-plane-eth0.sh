#!/bin/sh

set -ex

sudo kubeadm config images pull

sudo kubeadm init --config=/dev/stdin <<EOF
apiVersion: kubeadm.k8s.io/v1beta4
kind: InitConfiguration
---
apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
networking:
  dnsDomain: cluster.local
  podSubnet: 10.244.0.0/16
  serviceSubnet: 10.96.0.0/12
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
failSwapOn: false
EOF

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl taint nodes $(hostname --long) node-role.kubernetes.io/control-plane:NoSchedule-
kubectl taint nodes $(hostname --long) node-role.kubernetes.io/control-plane:PreferNoSchedule

kubectl get all --all-namespaces
kubectl describe node

sudo kubeadm token list
sudo kubeadm token create --print-join-command

# eof
