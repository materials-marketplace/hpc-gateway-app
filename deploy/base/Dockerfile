FROM python:3.8

WORKDIR /app

# Copy repo contents
COPY hpc_gateway/ ./hpc_gateway
COPY app.py setup.cfg setup.py ./

RUN pip install -U pip setuptools wheel \
    && pip install -e .

COPY .docker/run.sh ./

CMD ["/app/run.sh"]
