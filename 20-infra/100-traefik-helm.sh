#!/bin/sh

set -ex

helm repo add traefik https://traefik.github.io/charts
helm repo update

{
  printf '%s\n' \
    'apiVersion: v1' \
    'kind: Namespace' \
    'metadata:' \
    '  name: traefik' \
    '  labels:' \
    '    pod-security.kubernetes.io/enforce: privileged' \
    '    pod-security.kubernetes.io/audit: baseline' \
    '    pod-security.kubernetes.io/warn: baseline' \
    '---'
  helm --namespace traefik template traefik traefik/traefik \
    --set deployment.kind=DaemonSet \
    --set service.spec.type=ClusterIP \
    --set ingressClass.isDefaultClass=false \
    --set ports.web.hostPort=80 \
    --set ports.websecure.hostPort=443 \
    --set resources.requests.cpu=100m \
    --set resources.requests.memory=64Mi \
    --set   resources.limits.memory=256Mi \
    --set-string 'nodeSelector.m0net/infralab=true'
} > 20-infra/110-traefik.yaml

# kubectl rollout status -n traefik ds/traefik

# eof
