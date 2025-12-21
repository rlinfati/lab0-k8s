# Load Balancer

kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/refs/heads/v0.15/config/manifests/metallb-native.yaml
# FIX https://github.com/metallb/metallb/branches/active

kubectl label node $(hostname --long) node.kubernetes.io/exclude-from-external-load-balancers-

kubectl get configmap kube-proxy -n kube-system -o yaml | \
sed -e "s/strictARP: false/strictARP: true/" | \
kubectl apply -f - -n kube-system

kubectl -n metallb-system get all
kubectl -n metallb-system logs deployment.apps/controller
