import random
import string
from json import loads

from kubernetes import client, config
import tipos
#import paho.mqtt.client as mqtt
import os
import sys
import time
import kafka

# Parámetros de la configuración del objeto
namespace = "default"


MQTT_HOST = "mosquitto"
USER = 'admin'
PASSWORD = 'mosquittoGCIS'
IP_BROKER = "192.168.1.1"
APPEVENTS_TOPIC='ApplicationEvents'

# def subscriber_mqtt():
#
#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("Connected to MQTT broker.")
#             global connected
#             connected = True
#         else:
#             print("Connection failed: ") + str(rc)
#         sys.stdout.flush()
#
#     def on_message(client, userdata, message):
#         print("Datos del topico: " + str(message.topic))
#         print(message.payload)
#         raise_application_event2k8s_event(message)
#
#     clientMqtt = mqtt.Client()
#     clientMqtt.username_pw_set(USER, password=PASSWORD)
#     clientMqtt.connect(IP_BROKER, 31883)
#     clientMqtt.loop_start()
#     clientMqtt.subscribe(APPEVENTS_TOPIC, qos=0)
#     clientMqtt.on_connect = on_connect
#     clientMqtt.on_message = on_message
#     while True:
#         pass

def subscriber_kafka():
    IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"
    consumer = kafka.KafkaConsumer('ApplicationEvents', bootstrap_servers=[IP_server + ':9092'],value_deserializer=lambda x: loads(x.decode('utf-8')), client_id='appevents-consumer')
    while True:
        for msg in consumer:
            print('He recibido algo:')
            print(msg)
            raise_application_event2k8s_event(msg)

def event_parser(message):
    event = tipos.evento('Este es un evento simulado para poner en ejecucion una aplicacion.', 'AplicacionDesplegada',
                         'app' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)), 'Test')
    # event['action'] = 'DESPLEGAR'

    aux={
        'source' : {
        'component': message['CONTEXT']['source'],
    },
        'metadata':{
            'name' : message['CONTEXT']['source']+'-'+message['CONTEXT']['id']+'-event',
            'annotations':{
                'data' : message['DATA']
            },
            'labels': {
                'cause': 'ehu.gcis'
            }
        },
    }

    event['action'] = message['CONTEXT']['type']
    event['event_time'] = message['CONTEXT']['time']
    event['message'] = message['CONTEXT']['type']
    event['reason'] = 'CloudEvent '+message['CONTEXT']['specversion'] +' caused by ' + message['CONTEXT']['subject']
    event['reporting_component'] = message['CONTEXT']['source']
    event['type']=message['CONTEXT']['type']
    event.update(aux)

    return event

def raise_application_event2k8s_event(message): #Debería discriminar de alguna forma el mensaje que le llega, que imagino será diferente desde MQTT o Kafka.
    k8s_client = client.CoreV1Api()

    #Ojo esto está programado para los mensajes que le lleguen por MQTT, para los mensajes de Kafka habrá que hacerlo distinto.
    decodedMessage = loads(message.payload.decode('utf-8'))

    k8s_event = event_parser(decodedMessage)
    k8s_client.create_namespaced_event(namespace, k8s_event)  # Creamos el Kubernetes Event

def application_events_watcher():
    #subscriber_mqtt()
    subscriber_kafka()

def triggerer():
    # TODO Forma para utilizar desde Pycharm
    #path = os.path.abspath(os.path.dirname(__file__))
    #path = path.replace('EventOperator\\Python_Scripts', "")
    #config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster
    # config.load_kube_config("/etc/rancher/k3s/k3s.yaml")  # Cargamos la configuracion del cluster
    config.load_incluster_config()
    application_events_watcher()

if __name__ == '__main__':
	triggerer()