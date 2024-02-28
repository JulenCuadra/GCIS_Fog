FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install kafka-python
COPY ./././Python_Scripts/Simulated_Action_InCluster.py /
CMD python3 Simulated_Action_InCluster.py