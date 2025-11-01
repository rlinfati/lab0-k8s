#!/bin/sh

set -ex

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

kubectl -n cert-manager patch deploy cert-manager --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--feature-gates=ACMEHTTP01IngressPathTypeExact=false"}
]'

# eof
