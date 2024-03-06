FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install pytz
RUN pip install datetime
COPY mi_controlador_componentes.py /
COPY tipos.py /
COPY component_definition.yaml /CRD/

WORKDIR /

CMD python3 mi_controlador_componentes.py