echo "########## INSTALLING K3S MASTER ON HOST ##########"
host_ip = "master" # alias
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" sh -s - --node-ip $host_ip # El maestro tiene una ip fija 192.168.1.1
echo

echo "########## SCANNING AVAILABLE NODES ##########" # Que todos los workers encendidos se incluyan en el cluster.
number = 11
for i in $(seq 1 $number)
do
  node_ip = "worker"$i
  ping -c 1 $node_ip &> /dev/null
  if [[ $? -ne 0 ]]; then
    echo "ERROR: "$node_ip" not available"
  else 
    echo "########## INSTALLING K3S AGENT ON "$node_ip" ##########"
    k3s_token=$(sudo cat /var/lib/rancher/k3s/server/node-token)
    remote_cmd="'curl -sfL https://get.k3s.io | K3S_URL=https://"$host_ip":6443 K3S_TOKEN="$k3s_token" sh -s - --node-label node-type=worker'" # Quizás podamos poner varios labels para facilitarle la vida a Camilo en su futuro despliegue.
    echo $remote_cmd
    ssh -o StrictHostKeyChecking=no ubuntu@$node_ip \'$remote_cmd\' # El ssh sería directamente a workeri
    echo
  fi
done
