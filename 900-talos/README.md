# README.md

export TALOSCP=172.16.91.101

talosctl gen secrets -o CLUSTER-secrets.yaml

talosctl gen config cluster.local https://$TALOSCP:6443 \
    --with-secrets CLUSTER-secrets.yaml \
    --talos-version 1.11 \
    --output-types talosconfig \
    --output CLUSTER-talosconfig

# single controlplane and worker node
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets CLUSTER-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @TALOS-disk.yaml \
    --config-patch @TALOS-dns.yaml \
    --config-patch-control-plane @TALOS-cpallowpod.yaml \
    --config-patch-control-plane @TALOS-node-cp101.yaml \
    --output-types controlplane \
    --output CLUSTER-controlplane-101.yaml

# one controlplane plus two worker
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets CLUSTER-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @TALOS-disk.yaml \
    --config-patch @TALOS-dns.yaml \
    --config-patch-control-plane @TALOS-node-cp101.yaml \
    --output-types controlplane \
    --output CLUSTER-controlplane-101.yaml
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets CLUSTER-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @TALOS-disk.yaml \
    --config-patch @TALOS-dns.yaml \
    --config-patch-worker @TALOS-node-w111.yaml \
    --output-types worker \
    --output CLUSTER-worker-111.yaml
talosctl gen config cluster.local https://$TALOSCP:6443 \
    --install-disk /dev/nvme0n1 \
    --with-docs=false \
    --with-secrets CLUSTER-secrets.yaml \
    --kubernetes-version 1.34.1 \
    --talos-version 1.11 \
    --config-patch @TALOS-disk.yaml \
    --config-patch @TALOS-dns.yaml \
    --config-patch-worker @TALOS-node-w112.yaml \
    --output-types worker \
    --output CLUSTER-worker-112.yaml

export TALOSIP=172.16.91.129
talosctl get links --insecure --nodes $TALOSIP
talosctl get disks --insecure --nodes $TALOSIP
talosctl get discoveredvolumes --insecure --nodes $TALOSIP
talosctl get volumestatus --insecure --nodes $TALOSIP
talosctl get mountstatus --insecure --nodes $TALOSIP
talosctl apply-config --insecure --nodes $TALOSIP --file CLUSTER-controlplane-101.yaml
talosctl apply-config --insecure --nodes $TALOSIP --file CLUSTER-worker-111.yaml
talosctl apply-config --insecure --nodes $TALOSIP --file CLUSTER-worker-112.yaml

rm $HOME/.talos/config
talosctl config merge CLUSTER-talosconfig
talosctl config endpoints $TALOSCP
talosctl config node $TALOSCP
talosctl config contexts

talosctl bootstrap

rm $HOME/.kube/config
talosctl kubeconfig

talosctl upgrade --stage
talosctl upgrade-k8s --pre-pull-images
