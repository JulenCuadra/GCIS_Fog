FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install pytz
RUN pip install datetime
COPY mi_controlador_aplicaciones.py /
COPY tipos.py /
COPY application_definition.yaml /CRD/

WORKDIR /

CMD python3 mi_controlador_aplicaciones.py