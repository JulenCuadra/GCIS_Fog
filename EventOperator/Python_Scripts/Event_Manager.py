from kubernetes import client, config, watch
import tipos
import os
import random
import string

# Parámetros de la configuración del objeto
namespace = "default"
client_batch = client.BatchV1Api() #Creamos el cliente para interactuar con la API de Kubernetes, en concreto con los recursos de tipo batch, como el Job.
client_resources = client.CoreV1Api()

action_list = {}#Valorar volcar esto a un ConfigMap, que el ¿Controlador de componentes rellene ese configmap? En el caso de que no se use nuestra extensión deberían declarar ese listado de acciones al ConfigMap de alguna forma distinta.
action_list = {'dummy-action', 'not-dummy-action'}
def update_action_list():
    #TODO leería el ConfigMap y volcaría el listado de acciones disponibles a este gestor.
    #TODO cuándo debería hacerlo?
    pass

def cache_available_actions():
    for action in action_list:
        #TODO ver https://github.com/senthilrch/kube-fledged que ya se encarga de este problema.
        #Todo otra opción es crear un daemonset que mande el contenedor a sleep y entonces ya está cacheado.
        pass

def pasar_a_ejecucion(nombre):
    job=tipos.job_pasar_a_ejecucion(nombre)
    cliente_batch=client.BatchV1Api()
    cliente_batch.create_namespaced_job(namespace, job)

def action_is_available(action_name):
    checked = False
    #Comprobar que la acción está disponible de entre las acciones conocidas.
    #TODO al usar el configmap el listado de acciones va a estar en un fichero en /config/
    if action_name in action_list:
        checked = True
    return checked

def handle_event(event, action): #Tanto el evento como la accion tienen el formato de Kubernetes.
    client_batch = client.BatchV1Api()#TODO Modificar porque no tiene sentido que se cree varias veces
    if action_is_available(action['name']):
        job = tipos.job_event_handler(event.metadata.name + action['name'] + '-'.join(random.choices(string.ascii_lowercase + string.digits, k=5)))
        job['spec']['template']['spec']['containers'][0]['image'] = action['image']
        job['spec']['template']['spec']['containers'][0]['imagePullPolicy'] = 'Always'
        job['spec']['template']['spec']['containers'][0]['env'][0][
            'customization'] = action['customization'] #OJO es un array habría que pasarlo como tal.
        client_batch.create_namespaced_job(namespace, job)


def check_event_action_relationships(source,event):
    client_customresources = client.CustomObjectsApi()#TODO modificar esto porque no tiene sentido clearlo varias veces.
    #TODO, las proximas sentencias serán distintas para los recursos externos a nuestra extensión.
    source_split = source.split('/')
    app_structure_levels = 3#len(source_split)-2 #TODO checkear para casos de app y comp solo
    i=app_structure_levels
    while i >= 1:
        if i==app_structure_levels:
            comp_name = source_split[-i]
        else:
            comp_name = comp_name + '-' +source_split[-i]
        i-=1
    resource = client_customresources.get_namespaced_custom_object('ehu.gcis.org','v1alpha1','default','components',comp_name)#todo obtener la parte final del source para nombre de componente
    event_action_list = resource['spec']['events']
    for listed_event in event_action_list:
        if event.metadata.name in listed_event['name']: #Si el nombre del evento está entre el listado de eventos del recurso.
            for action in listed_event['actions']: #Por cada acción asociada a ese evento.
                handle_event(event, action)
            pass

def watcher_events(client):
    watcher = watch.Watch()
    for event in watcher.stream(client.list_event_for_all_namespaces):
        #TODO evaluar si merece la pena añadir a los eventos un label para hacer esta discriminación o si dejarlo discriminado en la action. Probado con label.
        #TODO el event manager debería acceder al recurso componente y ver la relación entre evento y sus acciones. Creada una función para checkear esto.
        #TODO ver como podría el event manager saber que acciones hay que cachear. Ver evento de recurso creado, obtener ese recurso y ver si tiene eventos, leer sus acciones y cachearlas.
        #TODO ver como el event manager podría conocer el listado de acciones disponibles
        objeto = event['object']
        tipo = event['type']
        print("Nuevo evento: ", "Hora del evento: ", objeto.first_timestamp, "Tipo de evento: ", tipo, "Motivo:", objeto.reason, "Mensaje:", objeto.message)


        if objeto.metadata.labels:
            if 'cause' in objeto.metadata.labels:
                if objeto.metadata.labels['cause'] == 'ehu.gcis': #Si el evento ha sido lanzado por un recurso nuestro.
                    check_event_action_relationships(objeto.source.component,objeto)
                elif objeto.metadata.labels['cause'] == 'external': # Cause existe pero no es de ehu.gcis, se presupone que no utilizan nuestra extensión.
                    check_event_action_relationships(objeto.source.component,objeto) #TODO, el triggerer deberá generar un
                else: #Hay un label cause pero no es de nuestra extension event driven
                    pass

#TODO el gestor debería tener dos hilos, uno de ellos para el watcher de eventos y otro para cachear las acciones y actualizar su listado.
#Si utilizamos kube fledged no haría falta  este segundo hilo.
def action_manager():
    update_action_list()
    cache_available_actions()
def gestor():
    # TODO Forma para utilizar desde Pycharm
    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace('EventOperator\\Python_Scripts', "")
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster
    #config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    #config.load_incluster_config() #Forma para obtener la configuración desde dentro del cluster.
    watcher_events(client.CoreV1Api())


if __name__ == '__main__':
	gestor()