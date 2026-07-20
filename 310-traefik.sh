#!/bin/sh

set -ex

sudo firewall-cmd --permanent --zone=public --add-service=http --add-service=https
sudo firewall-cmd             --zone=public --add-service=http --add-service=https
sudo firewall-cmd --zone=public --list-all

# local repo
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
    --set deployment.kind=Deployment \
    --set service.spec.type=ClusterIP \
    --set ports.web.hostPort=80 \
    --set ports.websecure.hostPort=443 \
} | sed '/helm\.sh\/chart/d' > 312-traefik.yaml

# install traefik
kubectl apply -f 312-traefix.yaml

# cabhs.srv - lab0x86.m0.cl - 192.99.45.132
kubectl -n traefik patch svc traefik --type='json' -p='[{"op":"add","path":"/spec/externalIPs","value":["192.99.45.132"]}]'
# clval.vps - lab0arm.m0.cl - 172.30.16.3
kubectl -n traefik patch svc traefik --type='json' -p='[{"op":"add","path":"/spec/externalIPs","value":["172.30.16.3"]}]'
# fenix.ubb - lab017a.m0.cl - 146.83.193.155
kubectl -n traefik patch svc traefik --type='json' -p='[{"op":"add","path":"/spec/externalIPs","value":["146.83.193.155"]}]'
# radio.ubb - lab023a.m0.cl - 146.83.193.156
kubectl -n traefik patch svc traefik --type='json' -p='[{"op":"add","path":"/spec/externalIPs","value":["146.83.193.156"]}]'
# reloj.ubb - lab025a.m0.cl - 146.83.193.157
kubectl -n traefik patch svc traefik --type='json' -p='[{"op":"add","path":"/spec/externalIPs","value":["146.83.193.157"]}]'

# eof
