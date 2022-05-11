from kubernetes import client, config
import kafka
import random
import time

def func_productor():
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
    productor = kafka.KafkaProducer(bootstrap_servers=IP_server + ':9092', client_id='mi-productor-prueba')
    #test=productor.bootstrap_connected()
    a=1
    while True:
        numero = random.randrange(0,10,1)
        time.sleep(2)
        print(numero)
        productor.send('topico-datos-crudos', b'Hola')
        productor.flush()
        a=1

if __name__ == '__main__':
    func_productor()