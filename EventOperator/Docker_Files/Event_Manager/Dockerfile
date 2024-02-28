FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip pytz
COPY Event_Manager.py /
COPY tipos.py /
CMD python3 Event_Manager.py