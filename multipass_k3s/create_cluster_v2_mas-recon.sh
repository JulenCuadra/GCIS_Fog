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

echo "########## DOWNLOADING JADE LIB AND COPYING IT TO SHARED FOLDER ##########"
curl -o jade-bin.zip https://jade.tilab.com/dl.php?file=JADE-bin-4.5.0.zip && unzip jade-bin.zip
mv jade/lib shared/
echo

echo "########## STARTING JADE MAIN CONTAINER ##########"
sudo apt install openjdk-8-jre-headless
host_ip=$(ifconfig mpqemubr0 | grep "inet " | awk -F: '{print $1}' | awk '{print $2}')
java -cp "shared/lib/jade.jar" jade.Boot -gui -local-host $host_ip &
sleep 5
echo

echo "########## CREATING NODES ##########"
read -p "Enter number of nodes: " number
for i in $(seq 1 $number)
do
  node_name=""
  if [ $i -le 9 ]
  then
    node_name="node00"$i
  else
    node_name="node0"$i
  fi
  echo "########## CREATING "$node_name" ##########"
  multipass launch --name $node_name --cpus 2 --mem 1G --disk 3G --cloud-init multipass.yaml 
  echo
  
  echo "########## MOUNTING SHARED FOLDER ON "$node_name" MULTIPASS INSTANCE ##########"
  multipass mount shared $node_name
  echo
  
  echo "########## STARTING PROCESING NODE ON "$node_name" ##########"
  node_ip="$(multipass list | tail -n -1 | awk '{ print $3 }')"
  ssh -o StrictHostKeyChecking=no ubuntu@$node_ip "sudo apt update && sudo apt install openjdk-8-jre-headless -y"
  me=$(whoami)
  remote_cmd="'java -cp \"/home/"$me"/shared/lib/jade.jar\" jade.Boot -container -host "$host_ip" -local-host "$node_ip" "$node_name":jade.tools.DummyAgent.DummyAgent'"
  echo $remote_cmd
  ssh -o StrictHostKeyChecking=no ubuntu@$node_ip \'$remote_cmd\' &
  sleep 5
  echo
  
  free -m && sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' && free -m
  echo
done
