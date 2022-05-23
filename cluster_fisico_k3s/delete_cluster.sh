#!/bin/bash
echo "########## DELETING K3S FROM THE CLUSTER ##########"
kubectl delete deploy --all
kubectl delete nodes --all
echo "########## SCANNING AVAILABLE NODES ##########"
number=11
for i in $(seq 1 $number)
do
  node_ip="worker"$i
  ping -c 1 $node_ip &> /dev/null
  if [[ $? -ne 0 ]]; then
    echo "ERROR: "$node_ip" not available"
  else
    echo "########## UNINSTALLING K3S AGENT ON "$node_ip" ##########"
    remote_cmd="'echo 123lau | sudo -S /usr/local/bin/k3s-agent-uninstall.sh'"
    echo $remote_cmd
    ssh -o StrictHostKeyChecking=no $node_ip \'$remote_cmd\'
    echo
    remote_cmd="'echo 123lau | sudo -S rm -rf /var/lib/rancher/k3s'"
    echo
    ssh -o StrictHostKeyChecking=no $node_ip \'$remote_cmd\'
    echo
  fi
done

echo "########## UNINSTALLING K3S FROM THE MASTER ##########"
sudo /usr/local/bin/k3s-uninstall.sh
sudo rm -rf /var/lib/rancher/k3s
