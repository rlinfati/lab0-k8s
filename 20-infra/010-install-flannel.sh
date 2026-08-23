#!/bin/sh

set -ex

echo br_netfilter | sudo tee /etc/modules-load.d/kube-flannel.conf
sudo modprobe br_netfilter

kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"  internal="}{.status.addresses[?(@.type=="InternalIP")].address}{"  flannel="}{.metadata.annotations.flannel\.alpha\.coreos\.com/public-ip}{"\n"}{end}'

# eof
