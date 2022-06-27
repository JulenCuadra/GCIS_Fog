Este repositorio contiene la documentación relativa al demostrador.

Falta la carpeta .vs ya que no cabe en Github.

Anotaciones sobre puesta en marcha del proyecto:

  - Esta demostración necesita tener un bróker desplegado (En nuestro caso, en el clúster físico.)
  - El NodePort que expone el bróker desplegado en el clúster, hace que puedas acceder a el bróker apuntando a cualquier nodo de Kubernetes y a su puerto NodePort.
  - La compartición de información entre la función de ODK y el FB se hace a través de memoria compartida. Los cambios que uno hagan a esa zona de memoria los verá el otro.
  - Las funciones de la app ODK se ejecutan cuando se solicita desde el FB. 
  - El FB no espera a que se ejecute la función si no que sigue con su ciclo normal de funcionamiento.
  - Un QoS de 0, no espera a recibir confirmación de recepción. No se ejecuta el callback delivered().
  - Es necesario añadir al PATH de Windows los directorios bin de paho-c y paho-cpp en el ordenador en el que vaya a ejecutarse la app ODK.
  - Desde el fichero cpp de ODK, tener cuidado con añadir estructuras nuevas de datos, ficheros ODK_Types y .odk.
 
