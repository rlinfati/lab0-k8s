#!/bin/sh

set -ex

sudo kubeadm config images pull

K8SIP="$(tailscale ip -4)"
APIIP="100.64.128.131" &&
TOKEN="abcdef.0123456789abcdef" &&
sudo kubeadm join --config=/dev/stdin <<EOF
apiVersion: kubeadm.k8s.io/v1beta4
kind: JoinConfiguration
discovery:
  bootstrapToken:
    apiServerEndpoint: "${APIIP}:6443"
    token: "${TOKEN}"
    unsafeSkipCAVerification: true
nodeRegistration:
  kubeletExtraArgs:
    - name: node-ip
      value: "${K8SIP}"
EOF

kubectl get all --all-namespaces
kubectl describe node

# eof
