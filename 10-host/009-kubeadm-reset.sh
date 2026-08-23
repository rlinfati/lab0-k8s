#!/bin/sh

set -ex

sudo kubeadm reset --cleanup-tmp-dir
rm -r $HOME/.kube

sudo crictl rmp --all
sudo crictl rm --all
sudo crictl rmi --prune
sudo crictl rmi --all

# eof
