#!/bin/sh

set -ex

sudo firewall-cmd --permanent --zone=public --add-service=http --add-service=https
sudo firewall-cmd             --zone=public --add-service=http --add-service=https
sudo firewall-cmd --zone=public --list-all

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/refs/heads/main/deploy/static/provider/cloud/deploy.yaml

kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"replace","path":"/spec/type","value":"ClusterIP"}
]'

# cabhs.srv
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["192.99.45.132"]}
]'
# clval.vps
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["172.30.16.3"]}
]'
# fenix.ubb
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.155"]}
]'
# radio.ubb
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.156"]}
]'
# reloj.ubb
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.157"]}
]'
# synco.ubb
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.158"]}
]'
# hostPort
kubectl -n ingress-nginx patch deploy ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/ports/0/hostPort","value":80},
  {"op":"add","path":"/spec/template/spec/containers/0/ports/1/hostPort","value":443}
]'

# eof
