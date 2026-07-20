#!/bin/sh

set -ex

sudo firewall-cmd --permanent --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd --permanent --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd             --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd             --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd --zone=trusted --list-all

# sudo nmcli connection add type dummy ifname k8s0 con-name k8s0 ipv4.addresses 100.255.100.255/32 ipv4.method manual
# sudo nmcli connection up k8s0

sudo kubeadm config images pull
sudo kubeadm init --pod-network-cidr 10.244.0.0/16 --service-cidr 10.96.0.0/12 --dry-run
sudo kubeadm init --config NoSwap.yaml

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl taint nodes $(hostname --long) node-role.kubernetes.io/control-plane:NoSchedule-

echo br_netfilter | sudo tee /etc/modules-load.d/kube-flannel.conf
sudo modprobe br_netfilter

kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
kubectl get cm -n kube-system kubeadm-config -o yaml | grep Subnet

kubectl get all -A
kubectl describe node
sudo crictl stats

# eof
