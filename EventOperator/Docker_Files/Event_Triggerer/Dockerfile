FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install kafka-python
RUN pip pytz
COPY Event_Triggerer.py /
COPY tipos.py /
CMD python3 Event_Triggerer.py