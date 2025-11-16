#!/bin/sh

set -ex

sudo firewall-cmd --permanent --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd --permanent --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd             --zone=trusted --add-source=10.244.0.0/16
sudo firewall-cmd             --zone=trusted --add-source=10.96.0.0/12
sudo firewall-cmd --zone=trusted --list-all

### rhel10 SELinux BPF policy workaround
### allow init_t container_runtime_t:bpf prog_run;
### sudo ausearch -c 'systemd' --raw | audit2allow -M my-systemd
### sudo semodule -i my-systemd.pp

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

# eof
