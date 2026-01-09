#!/bin/sh

set -ex

sudo grubby --update-kernel=ALL --remove-args="rhgb"

# FIX: fenix
# sudo grubby --update-kernel=ALL --args="reboot=efi"
# sudo grubby --update-kernel=ALL --remove-args="reboot=efi"
# reboot=efi reboot=acpi reboot=pci

# FIX: ntp ubiobio
# sudo chronyc -a "add server ntp.ubiobio.cl iburst"
# sudo chronyc -a makestep
# sudo chronyc sources -v
# sudo chronyc tracking

curl https://download.opensuse.org/repositories/isv:/cri-o:/stable:/v1.34/rpm/isv:cri-o:stable:v1.34.repo                      | sudo tee /etc/yum.repos.d/cri-o.repo
curl https://download.opensuse.org/repositories/isv:/kubernetes:/core:/stable:/v1.34/rpm/isv:kubernetes:core:stable:v1.34.repo | sudo tee /etc/yum.repos.d/kubernetes.repo

echo net.ipv4.ip_forward = 1 | sudo tee /etc/sysctl.d/kubernetes.conf
sudo sysctl --system

sudo dnf install cri-o kubelet kubeadm kubectl
sudo systemctl enable --now crio
sudo systemctl enable --now kubelet

# eof
