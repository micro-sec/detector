echo "Do not run this script."
exit 1

kubeadm reset

swapoff -a


# Check if systemd is the cgroup driver being used
kubeadm init --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=all --v=5


mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/k8s-manifests/kube-flannel-rbac.yml

kubeadm join --token TOKEN MASTER_IP:6443