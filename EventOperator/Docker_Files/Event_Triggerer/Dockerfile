FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install kafka-python
COPY ./././Python_Scripts/Event_Triggerer.py /
CMD python3 Event_Triggerer.py