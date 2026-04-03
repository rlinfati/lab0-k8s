#!/bin/sh

set -ex

sudo firewall-cmd --permanent --zone=public --add-service=http --add-service=https
sudo firewall-cmd             --zone=public --add-service=http --add-service=https
sudo firewall-cmd --zone=public --list-all

# local repo
helm repo add traefik https://traefik.github.io/charts
helm repo update

(echo 'apiVersion: v1\nkind: Namespace\nmetadata:\n  name: traefik' && 
helm --namespace traefik template traefik traefik/traefik --set service.type=ClusterIP) > 312-traefix.yaml

# delete ingress-nginx
# kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/refs/heads/main/deploy/static/provider/cloud/deploy.yaml

# install traefik
kubectl apply -f 312-traefix.yaml

# cabhs.srv - lab0x86.m0.cl - 192.99.45.132
kubectl -n traefik patch svc traefik --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["192.99.45.132"]}
]'
# clval.vps - lab0arm.m0.cl - 172.30.16.3
kubectl -n traefik patch svc traefik --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["172.30.16.3"]}
]'
# fenix.ubb - lab017a.m0.cl - 146.83.193.155
kubectl -n traefik patch svc traefik --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.155"]}
]'
# radio.ubb - lab023a.m0.cl - 146.83.193.156
kubectl -n traefik patch svc traefik --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.156"]}
]'
# reloj.ubb - lab025a.m0.cl - 146.83.193.157
kubectl -n traefik patch svc traefik --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.157"]}
]'
# hostPort
kubectl -n traefik patch deploy traefik --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/ports/0/hostPort","value":80},
  {"op":"add","path":"/spec/template/spec/containers/0/ports/1/hostPort","value":443}
]'

# eof
