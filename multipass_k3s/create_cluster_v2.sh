echo "########## ADDING YOUR USER TO SUDOERS FILE ##########"
echo "If you already have added your current user to sudoers file,"
echo "you can skip this part and press any key to continue"
echo
echo "Otherwise, execute:"
echo "  echo \"username  ALL=(ALL) NOPASSWD:ALL\" | sudo tee /etc/sudoers.d/username"
echo "where 'username' is your current user"
read -p "And press Ctrl+C to execute the script again"
echo

echo "########## INSTALLING MULTIPASS ##########"
sudo snap install multipass
echo

echo "########## GENERATING KEYS ##########"
echo "If you already have ~/.ssh/id_rsa and ~/.ssh/id_rsa.pub, you can skip this part"
echo
echo "Otherwise, execute 'ssh-keygen' to create a private/public key"
echo
read -p "Press any key to continue "
echo
pub_key=$(cat ~/.ssh/id_rsa.pub)
echo "ssh_authorized_keys:" > multipass.yaml
echo "  - "$pub_key >> multipass.yaml

echo "########## CREATING SHARED FOLDER AMONG HOST AND NODES ##########"
mkdir shared
echo

echo "########## INSTALLING K3S MASTER ON HOST ##########"
host_ip=$(ifconfig mpqemubr0 | grep "inet " | awk -F: '{print $1}' | awk '{print $2}')
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" sh -s - --node-ip $host_ip
echo

echo "########## DOWNLOADING JADE LIB AND COPYING IT TO SHARED FOLDER ##########"
curl -o jade-bin.zip https://jade.tilab.com/dl.php?file=JADE-bin-4.5.0.zip && unzip jade-bin.zip
curl -o jade-examples.zip https://jade.tilab.com/dl.php?file=JADE-examples-4.5.0.zip && unzip jade-examples.zip
mv jade/lib shared/
echo

echo "########## STARTING JADE MAIN CONTAINER ##########"
sudo apt install openjdk-8-jre-headless
java -cp "shared/lib/jade.jar" jade.Boot -gui -local-host $host_ip &
sleep 5

echo "########## CREATING NODES ##########"
read -p "Enter number of nodes: " number
for i in $(seq 1 $number)
do
  if [ $i -le 9 ]
  then
    node_name="node00"$i
    echo "########## CREATING "$node_name" ##########"
    multipass launch --name $node_name --cpus 2 --mem 549M --disk 3G --cloud-init multipass.yaml 
  else
    node_name="node0"$i
    echo "########## CREATING "$node_name" ##########"
    multipass launch --name $node_name --cpus 2 --mem 549M --disk 3G --cloud-init multipass.yaml 
  fi
  echo
  
  echo "########## MOUNTING SHARED FOLDER ON "$node_name" MULTIPASS INSTANCE ##########"
  multipass mount shared $node_name
  echo
  
  echo "########## INSTALLING K3S AGENT ON "$node_name" ##########"
  node_ip="$(multipass list | tail -n -1 | awk '{ print $3 }')"
  k3s_token=$(sudo cat /var/lib/rancher/k3s/server/node-token)
  remote_cmd="'curl -sfL https://get.k3s.io | K3S_URL=https://"$host_ip":6443 K3S_TOKEN="$k3s_token" sh -'"
  ssh -o StrictHostKeyChecking=no ubuntu@$node_ip \'$remote_cmd\'
  echo
  
  echo "########## STARTING PROCESING NODE ON "$node_name" ##########"
  ssh -o StrictHostKeyChecking=no ubuntu@$node_ip "sudo apt update && sudo apt install openjdk-8-jre-headless -y"
  me=$(whoami)
  remote_cmd="'java -cp \"/home/"$me"/shared/lib/jade.jar:/home/"$me"/shared/lib/jadeExamples.jar\" jade.Boot -container -host "$host_ip" -local-host "$node_ip" "$node_name":examples.PingAgent.PingAgent'"
  ssh -o StrictHostKeyChecking=no ubuntu@$node_ip \'$remote_cmd\' &
  sleep 5
  echo
  
  free -m && sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' && free -m
  echo
done
