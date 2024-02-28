import time

import paho.mqtt.client as mqtt
from json import dumps
import kafka
import random
import string
import datetime

MQTT_HOST = "mosquitto"
USER = 'admin'
PASSWORD = 'mosquittoGCIS'
IP_BROKER = "192.168.1.1"
IP_server = IP_BROKER #OJO, ahora mismo kafka solo es accesible desde el cluster.


#Con la idea de utilizar una estructura de datos con la que las aplicaciones (en especial sus componentes),
#sean capaces de comunicarle al triggerer  a traves de Kafka cual es el evento detectado.
#La clasificacion de los eventos se hará en función del parámetro "Action"
Application_Event_Message = {
    'trigger' : {
        'App_Name' : 'AppTest',
        'Comp_Name' : 'CompTest',
        'Action' : 'TEST',                   # Acciones: DeployApp, ConfComp, ConfApp, Deploy y Config de Niveles superiores??, KillApp, Alert (Que sería similar a crear una app efimera),
        'Reason' : 'Surpassed Threshold',
    },
    'data' : {
        'Received_Data' : 80,
        'Threshold' : 75
    }
}


CloudEvents_Application_Event_Message = {
    'CONTEXT' :{
        'id' : ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
        'source': '/gcis-ehu/residenciabilbo/habitacionsur/carlos/appheartrate/comp1', #TODO revisar formato URI-Reference, vale como string??
        'specversion' : '1.0.2',
        'type' : 'reconfiguration',
        'subject' : 'threshold',
        'time' : datetime.datetime.now().timestamp(),
    },
    'DATA' : {
        'Received_Data' : 80,
        'Threshold' : 75
    }
}

def publish_application_event_mqtt():

    clientMqtt = mqtt.Client()
    clientMqtt.username_pw_set(USER, password=PASSWORD)
    clientMqtt.connect(IP_BROKER, 31883)
    clientMqtt.publish(topic='ApplicationEvents', payload=dumps(Application_Event_Message).encode('utf-8'))

def publish_application_event_kafka():

    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9090'], client_id='appevents-producer',
                                    value_serializer=lambda x: dumps(x).encode('utf-8')) #Problemas de conexión porque MQTT está expuesto como un NodePort pero Kafka lo tenemos con un ClusterIP.
    #Mensaje trasladado a Kafka según instrucciones de CloudEvents, mensaje estructurado.
    productor.send(topic='ApplicationEvents', key='ApplicationEvent', headers='content-type:application/cloudevents+json; charset=UTF-8', value=CloudEvents_Application_Event_Message)
    productor.flush()

if __name__ == '__main__':
    publish_application_event_mqtt()
    #publish_application_event_kafka()
    #TODO probar a mandar este mensaje a través de Kafka