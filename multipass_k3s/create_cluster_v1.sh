multipass launch --name master --cpus 2 --mem 2G --disk 3G --cloud-init multipass.yaml
multipass mount shared master
master_IP="$(multipass list | tail -n -1 | awk '{ print $3 }')"
k3sup install --ip $master_IP --user ubuntu --k3s-extra-args "--cluster-init"

for i in $(seq 1 2)
do
  if [ $i -le 9 ]
  then
    node_name="node00"$i
    echo "Creating "$node_name"..."
    multipass launch --name $node_name --cpus 1 --mem 549M --disk 3G --cloud-init multipass.yaml 
  else
    node_name="node0"$i
    echo "Creating "$node_name"..."
    multipass launch --name $node_name --cpus 1 --mem 549M --disk 3G --cloud-init multipass.yaml 
  fi
  multipass mount shared $node_name
  node_IP="$(multipass list | tail -n -1 | awk '{ print $3 }')"
  k3sup join --ip $node_IP --user ubuntu --server-ip $master_IP --server-user ubuntu 
  free -m && sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' && free -m
done
