#!/bin/sh

set -ex

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

kubectl get Issuers,ClusterIssuers,Certificates,CertificateRequests,Orders,Challenges --all-namespaces
kubectl delete CertificateRequests --all --all-namespaces

# eof
