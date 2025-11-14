#!/bin/sh

set -ex

cat 041-config-profiles.yaml | ssh synco.ubb.menoscero.com kubectl apply -f -
cat 042-config-jhub.yaml     | ssh synco.ubb.menoscero.com kubectl apply -f -
ssh synco.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_12cpu_120gb\": \"# burstable_12cpu_120gb\"}}'"
ssh synco.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_4cpu_30gb\":   \"# burstable_4cpu_30gb\"}}'"
ssh synco.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_1cpu_7gb\":    \"# burstable_1cpu_7gb\"}}'"
ssh synco.ubb.menoscero.com kubectl -n jupyterhub delete pod --all

cat 041-config-profiles.yaml | ssh cosyn.ubb.menoscero.com kubectl apply -f -
cat 042-config-jhub.yaml     | ssh cosyn.ubb.menoscero.com kubectl apply -f -
ssh cosyn.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_4cpu_30gb\": \"# burstable_4cpu_30gb\"}}'"
ssh cosyn.ubb.menoscero.com "kubectl -n jupyterhub patch configmap jhub.profiles --type merge -p '{\"data\": {\"burstable_1cpu_7gb\":  \"# burstable_1cpu_7gb\"}}'"
ssh cosyn.ubb.menoscero.com kubectl -n jupyterhub delete pod --all

cat 041-config-profiles.yaml | ssh grujh.menoscero.com kubectl apply -f -
cat 042-config-jhub.yaml     | ssh grujh.menoscero.com kubectl apply -f -
ssh grujh.menoscero.com kubectl -n jupyterhub delete pod --all

cat 041-config-profiles.yaml | ssh valjh.menoscero.com kubectl apply -f -
cat 042-config-jhub.yaml     | ssh valjh.menoscero.com kubectl apply -f -
ssh valjh.menoscero.com kubectl -n jupyterhub delete pod --all

# eof
