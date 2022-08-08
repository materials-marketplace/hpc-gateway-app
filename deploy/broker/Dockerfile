FROM python:3.8

WORKDIR /app

# Copy repo contents
COPY broker/requirements.txt broker/rpc_server.py ./

RUN pip install -r requirements.txt

CMD ["python ./rpc_server.py"]