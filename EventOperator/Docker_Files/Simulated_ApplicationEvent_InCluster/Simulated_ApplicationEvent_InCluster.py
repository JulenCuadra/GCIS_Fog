from json import dumps
from kubernetes import config
import kafka
import random
import string
import datetime
import time

IP_BROKER = "192.168.1.1"
IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"

CloudEvents_Application_Event_Message = {
    'CONTEXT' :{
        'id' : ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
        'source': '/gcis-ehu/dummy-residence/southroom-dummy-patient/dummy-app/dummy-component', #TODO revisar formato URI-Reference, vale como string??
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
def publish_application_event_kafka():
    print(CloudEvents_Application_Event_Message)

    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='appevents-producer',
                                    value_serializer=lambda x: dumps(x).encode('utf-8')) #Problemas de conexión porque MQTT está expuesto como un NodePort pero Kafka lo tenemos con un ClusterIP.
    #Mensaje trasladado a Kafka según instrucciones de CloudEvents, mensaje estructurado.
    productor.send(topic='ApplicationEvents', key=b'ApplicationEvent', value=CloudEvents_Application_Event_Message)
    # TODO añadir headers como tupla clave valor el valor en bytes , headers='content-type:application/cloudevents+json; charset=UTF-8'
    productor.flush()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    #config.load_incluster_config()
    publish_application_event_kafka()

    #TODO construir con Docker y subir al repositorio.
    #TODO preparar deployment para desplegar esto en el cluster.