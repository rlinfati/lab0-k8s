#!/bin/sh

set -ex

curl https://download.opensuse.org/repositories/isv:/cri-o:/stable:/v1.34/rpm/isv:cri-o:stable:v1.34.repo                      | sudo tee /etc/yum.repos.d/cri-o.repo
curl https://download.opensuse.org/repositories/isv:/kubernetes:/core:/stable:/v1.34/rpm/isv:kubernetes:core:stable:v1.34.repo | sudo tee /etc/yum.repos.d/kubernetes.repo

echo overlay      | sudo tee    /etc/modules-load.d/kubernetes.conf
echo br_netfilter | sudo tee -a /etc/modules-load.d/kubernetes.conf
sudo modprobe overlay
sudo modprobe br_netfilter

echo net.ipv4.ip_forward                 = 1 | sudo tee    /etc/sysctl.d/kubernetes.conf
echo net.bridge.bridge-nf-call-iptables  = 1 | sudo tee -a /etc/sysctl.d/kubernetes.conf
echo net.bridge.bridge-nf-call-ip6tables = 1 | sudo tee -a /etc/sysctl.d/kubernetes.conf
sudo sysctl --system

sudo dnf install cri-o kubelet kubeadm kubectl
sudo systemctl enable --now crio
sudo systemctl enable --now kubelet

# eof
