#!/bin/sh

set -ex

export TALOSCP=172.16.91.101

talosctl gen secrets -o 901-secrets.yaml

talosctl gen config cluster.local https://$TALOSCP:6443 \
    --with-secrets 901-secrets.yaml \
    --talos-version 1.11 \
    --output-types talosconfig \
    --output 901-talosconfig

# single controlplane and worker node
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets 901-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @902-disk.yaml \
    --config-patch @902-dns.yaml \
    --config-patch-control-plane @903-cpallowpod.yaml \
    --config-patch-control-plane @906-node-101cp.yaml \
    --output-types controlplane \
    --output 904-node-101-cp-w.yaml

# one controlplane plus three worker
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets 901-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @902-disk.yaml \
    --config-patch @902-dns.yaml \
    --config-patch-control-plane @906-node-101cp.yaml \
    --output-types controlplane \
    --output 905-node-101-cp.yaml
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets 901-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @902-disk.yaml \
    --config-patch @902-dns.yaml \
    --config-patch-worker @907-node-102w.yaml \
    --output-types worker \
    --output 905-node-102-w.yaml
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets 901-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @902-disk.yaml \
    --config-patch @902-dns.yaml \
    --config-patch-worker @908-node-103w.yaml \
    --output-types worker \
    --output 905-node-103-w.yaml
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets 901-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @902-disk.yaml \
    --config-patch @902-dns.yaml \
    --config-patch-worker @909-node-104w.yaml \
    --output-types worker \
    --output 905-node-104-w.yaml

export TALOSIP=172.16.91.129
talosctl get links --insecure --nodes $TALOSIP
talosctl get disks --insecure --nodes $TALOSIP
talosctl get discoveredvolumes --insecure --nodes $TALOSIP
talosctl get volumestatus --insecure --nodes $TALOSIP
talosctl get mountstatus --insecure --nodes $TALOSIP
talosctl apply-config --insecure --nodes $TALOSIP --file 904-node-101-cp-w.yaml
talosctl apply-config --insecure --nodes $TALOSIP --file 905-node-101-cp.yaml
talosctl apply-config --insecure --nodes $TALOSIP --file 905-node-102-w.yaml
talosctl apply-config --insecure --nodes $TALOSIP --file 905-node-103-w.yaml
talosctl apply-config --insecure --nodes $TALOSIP --file 905-node-104-w.yaml

rm $HOME/.talos/config
talosctl config merge 901-talosconfig
talosctl config endpoints $TALOSCP
talosctl config node $TALOSCP
talosctl config contexts

talosctl bootstrap

rm $HOME/.kube/config
talosctl kubeconfig

talosctl upgrade --stage
talosctl upgrade-k8s --pre-pull-images

# eof
