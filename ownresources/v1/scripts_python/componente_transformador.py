from kubernetes import client, config
import kafka
import random
import time

def func_transformador():
    config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    cliente = client.CoreV1Api()
    resp=cliente.list_namespaced_service("default")
    j = 0
    for i in resp.items:
        if 'bootstrap' in i.metadata.name:
            index = j
            break
        j = j + 1
    IP_server = resp.items[j].spec.cluster_ip
    consumidor = kafka.KafkaConsumer('topico-datos-crudos', bootstrap_servers= IP_server + ':9092')
    a=1
    while True:
        for msg in consumidor:
            print(msg)

if __name__ == '__main__':
    func_transformador()