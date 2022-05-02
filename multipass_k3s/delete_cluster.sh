export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
#sudo kubectl config set-context default
kubectl delete deploy --all
kubectl delete node --all
sudo /usr/local/bin/k3s-uninstall.sh
sudo rm -rf /var/lib/rancher/k3s

read -p "Enter number of nodes: " number
for i in $(seq 1 $number)
do
  if [ $i -le 9 ]
  then    echo "Deleting node00$i..."
    multipass delete node00$i
  else
    echo "Deleting node0$i..."
    multipass delete node0$i
  fi
done
multipass purge

