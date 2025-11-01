#!/bin/sh

set -ex

sudo kubeadm upgrade plan
sudo kubeadm config images pull
sudo kubeadm upgrade apply v....
sudo kubeadm upgrade node

# eof
