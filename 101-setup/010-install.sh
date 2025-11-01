#!/bin/sh

set -ex

curl https://download.opensuse.org/repositories/isv:/kubernetes:/addons:/cri-o:/stable:/v1.33:/build/rpm/isv:kubernetes:addons:cri-o:stable:v1.33:build.repo | sudo tee /etc/yum.repos.d/kubernetes-addons.repo
curl https://download.opensuse.org/repositories/isv:/kubernetes:/core:/stable:/v1.33/rpm/isv:kubernetes:core:stable:v1.33.repo                               | sudo tee /etc/yum.repos.d/kubernetes-core.repo

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
