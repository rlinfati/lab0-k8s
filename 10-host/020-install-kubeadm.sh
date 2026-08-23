#!/bin/sh

set -ex

# PKG_MANAGER apt dnf
PKG_MANAGER="dnf"
KUBERNETES_VERSION="v1.36"

if [ "$PKG_MANAGER" = "dnf" ]; then
    curl -fsSL "https://download.opensuse.org/repositories/isv:/cri-o:/stable:/${KUBERNETES_VERSION}/rpm/isv:cri-o:stable:${KUBERNETES_VERSION}.repo" \
        | sudo tee /etc/yum.repos.d/cri-o.repo >/dev/null
    curl -fsSL "https://download.opensuse.org/repositories/isv:/kubernetes:/core:/stable:/${KUBERNETES_VERSION}/rpm/isv:kubernetes:core:stable:${KUBERNETES_VERSION}.repo" \
        | sudo tee /etc/yum.repos.d/kubernetes.repo >/dev/null
else
    curl -fsSL "https://download.opensuse.org/repositories/isv:/cri-o:/stable:/${KUBERNETES_VERSION}/deb/Release.key" \
        | sudo gpg --dearmor --yes -o /usr/share/keyrings/cri-o-archive-keyring.gpg
    curl -fsSL "https://download.opensuse.org/repositories/isv:/kubernetes:/core:/stable:/${KUBERNETES_VERSION}/deb/Release.key" \
        | sudo gpg --dearmor --yes -o /usr/share/keyrings/kubernetes-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/cri-o-archive-keyring.gpg] https://download.opensuse.org/repositories/isv:/cri-o:/stable:/${KUBERNETES_VERSION}/deb/ /" \
        | sudo tee /etc/apt/sources.list.d/cri-o.list >/dev/null
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://download.opensuse.org/repositories/isv:/kubernetes:/core:/stable:/${KUBERNETES_VERSION}/deb/ /" \
        | sudo tee /etc/apt/sources.list.d/kubernetes.list >/dev/null
fi

echo "net.ipv4.ip_forward = 1" \
    | sudo tee /etc/sysctl.d/kubernetes.conf >/dev/null
sudo sysctl --system

if [ "$PKG_MANAGER" = "dnf" ]; then
    sudo dnf install -y cri-o cri-tools kubelet kubeadm kubectl
    sudo systemctl enable --now crio kubelet
else
    sudo apt-get update
    sudo apt install -y cri-o cri-tools kubelet kubeadm kubectl
fi

# eof
