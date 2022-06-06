#!/bin/bash
echo "########## INSTALLING K3S MASTER ON HOST ##########"
host_ip=192.168.1.1
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" sh -s - --node-ip $host_ip
echo

echo "########## SCANNING AVAILABLE NODES ##########"
number=11 # Numero de equipos que forman el cluster (sin contar al maestro).
k3s_token=$(sudo cat /var/lib/rancher/k3s/server/node-token)
echo K3S_URL=https://"$host_ip":6443 K3S_TOKEN="$k3s_token" sh - ./k3s_install.sh --node-label node-type=multipass > k3s_install_aux.sh 

for i in $(seq 1 $number)
do
  node_ip="worker"$i
  ping -c 1 $node_ip &> /dev/null
  if [[ $? -ne 0 ]]; then
    echo "ERROR: "$node_ip" not available"
  else
    echo "########## INSTALLING K3S AGENT ON "$node_ip" ##########"

    remote_cmd="'curl -sfL https://get.k3s.io --output k3s_install.sh'"
    echo $remote_cmd
    ssh -o StrictHostKeyChecking=no $node_ip \'$remote_cmd\' 

    remote_cmd="'chmod +x ./k3s_install.sh'"
    echo $remote_cmd
    ssh -o StrictHostKeyChecking=no $node_ip \'$remote_cmd\' 

    scp -o StrictHostKeyChecking=no ./k3s_install_aux.sh $node_ip:.

    remote_cmd="'chmod +x ./k3s_install_aux.sh'"
    echo $remote_cmd
    ssh -o StrictHostKeyChecking=no $node_ip \'$remote_cmd\' 

    remote_cmd="'echo 123lau | sudo -S ./k3s_install_aux.sh'" 
    echo $remote_cmd
    ssh -o StrictHostKeyChecking=no $node_ip \'$remote_cmd\'

    echo
  fi
done

