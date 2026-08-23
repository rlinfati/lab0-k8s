#!/bin/sh

set -ex

sudo firewall-cmd --permanent --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd --permanent --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd             --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd             --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd --zone=trusted --list-all

sudo kubeadm init --pod-network-cidr 10.244.0.0/16 --service-cidr 10.96.0.0/12 --dry-run
sudo kubeadm reset --cleanup-tmp-dir

# eof
