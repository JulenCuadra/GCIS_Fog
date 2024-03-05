from kubernetes import client, config
import time

grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

#TODO coger variables de entorno según me vengan.
#TODO modificar recurso para aplicar acción dummy que escriba un mensaje.

def action():
    contador = 0
    while contador < 5:
        config.load_incluster_config()
        cliente = client.CustomObjectsApi()
        print('Ejecutando acción correspondiente.')
        contador = contador +1
        time.sleep(1)

if __name__ == '__main__':
    action()