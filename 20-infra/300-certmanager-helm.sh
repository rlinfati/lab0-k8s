#!/bin/sh

set -ex

helm repo add cert-manager https://charts.jetstack.io
helm repo update

{
  printf '%s\n' \
    'apiVersion: v1' \
    'kind: Namespace' \
    'metadata:' \
    '  name: cert-manager' \
    '  labels:' \
    '    pod-security.kubernetes.io/enforce: baseline' \
    '    pod-security.kubernetes.io/audit: baseline' \
    '    pod-security.kubernetes.io/warn: baseline' \
    '---'
  helm --namespace cert-manager template cert-manager cert-manager/cert-manager \
    --set installCRDs=true \
    --set 'global.nodeSelector.m0net/infralab=true'
} > 20-infra/310-certmanager.yaml

# eof
