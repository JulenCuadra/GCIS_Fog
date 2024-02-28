import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
# import random
# import string
from json import loads
from kubernetes import client, config, watch
# import tipos
# import paho.mqtt.client as mqtt
import os
# import sys
# import time
# import kafka
# import asyncio

# Parámetros de la configuración del objeto
namespace = "default"

# Parámetros para conectarme a MQTT que de momento no se va a utilizar.
# MQTT_HOST = "mosquitto"
# USER = 'admin'
# PASSWORD = 'mosquittoGCIS'
# IP_BROKER = "192.168.1.1"
# APPEVENTS_TOPIC='ApplicationEvents'


# Parámetros para conectarme a InfluxDB.
token = "Bjalq1PTXXj77S2YYEyj-khoaKzW-_uwmOM_XDEQIFx_nIR2ekf7qi_Odq7dlVEM0H7QiNVr1WX6EwgY5JGKJQ==" #OJO esto cambia cada vez que se inicializa Influx, hay que ver cómo se puede leer desde aquí, imagino que algún Secret de Kubernetes.
org = "EHU"
url = "http://192.168.1.2:30086" # En este momento está desplegado en el worker1.
bucket = "test-bucket"

# Cliente para escritura en InfluxDB.
write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)
query_api = write_client.query_api() # Utilizada como testeo para ver si realmente estoy almacenando algo en InfluxDB.

#Suscriptores de MQTT y Kafka por si hiciesen falta, de momento no entran en la concepción.

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
#         store_application_event2k8s_event(message)
#
#     clientMqtt = mqtt.Client()
#     clientMqtt.username_pw_set(USER, password=PASSWORD)
#     clientMqtt.connect(IP_BROKER, 31883)
#     clientMqtt.loop_start()
#     clientMqtt.subscribe(APPEVENTS_TOPIC, qos=0)
#     clientMqtt.on_connect = on_connect
#     clientMqtt.on_message = on_message
#
# def subscriber_kafka():
#     IP_server = IP_BROKER
#     consumer = kafka.KafkaConsumer('ApplicationEvents', bootstrap_servers=[IP_server + ':9092'],
#                                      value_deserializer=lambda x: loads(x.decode('utf-8')), client_id='appevents-consumer')
#     while True:
#         for msg in consumer:
#             print('He recibido algo:')
#             print(msg)
#             store_application_event(msg)

def store_application_event(event):

    # decodedMessage = loads(event.payload.decode('utf-8'))
    object = event["object"]
    point = (Point("applicationevent")
             .tag("App_Name", "AppTest")
             .field("Action", object.action)
             .field("Message", object.message)
             .field("Reason", object.reason)
             .field("Threshold", 75)
             .time(object.event_time)) # Tiempo en el que se ha producido el evento, OJO hay que tener en cuenta el tiempo a nivel de generación, detección, disparo etc.
    write_api.write(bucket=bucket, org="EHU", record=point)

    #Lectura de la base de datos InfluxDB para comprobar si realmente estoy guardando algún dato.
    # query = """from(bucket: "test-bucket")
    #      |> range(start: -50m)
    #      |> filter(fn: (r) => r._field == "Dato_Medido")"""
    #
    # tables = query_api.query(query, org="EHU")

    # for table in tables:
    #     for record in table.records:
    #         print(record)
def application_events_watcher(): #TODO modificar para que no detecte o hable de application events sino de eventos en genérico.
    # Modificar para que le lleguen los eventos de Kubernetes, los discrimine en funcion del label y almacene esa info.
    # subscriber_mqtt()
    # while True:
    #     pass
    # subscriber_kafka()
    client_k8s = client.CoreV1Api()
    watcher = watch.Watch()
    for event in watcher.stream(client_k8s.list_namespaced_event,namespace):
        pass
        try: #Puede que el objeto no tenga labels, por lo que habria una exception.
            if "ehu-gcis" in event["object"].metadata.labels.values():
                print("ApplicationEvent detected, storing in InfluxDB.")
                store_application_event(event)
            else:
                print("Event not related to ApplicationEvents")
        except:
            print("Event not related to ApplicationEvents")

def logger():
    # TODO Forma para utilizar desde Pycharm
    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace('EventOperator\\Python_Scripts', "")
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster
    # config.load_kube_config("/etc/rancher/k3s/k3s.yaml")  # Cargamos la configuracion del cluster
    application_events_watcher()

if __name__ == '__main__':
	logger()