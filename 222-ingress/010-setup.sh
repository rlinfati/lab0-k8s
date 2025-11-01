#!/bin/sh

set -ex

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/refs/heads/main/deploy/static/provider/cloud/deploy.yaml

kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"replace","path":"/spec/type","value":"ClusterIP"}
]'

# grujh
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["172.30.101.187"]}
]'
# valjh
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["172.30.16.109"]}
]'
# synco.ubb
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.158"]}
]'
# cosyn.ubb
kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/externalIPs","value":["146.83.193.159"]}
]'
# hostPort
kubectl -n ingress-nginx patch deploy ingress-nginx-controller --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/ports/0/hostPort","value":80},
  {"op":"add","path":"/spec/template/spec/containers/0/ports/1/hostPort","value":443}
]'

# eof
