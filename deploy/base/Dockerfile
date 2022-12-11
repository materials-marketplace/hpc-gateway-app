FROM python:3.9

WORKDIR /app

# Copy repo contents
COPY . ./hpc-gateway-app

RUN pip install ./hpc-gateway-app[deploy]

WORKDIR /app/hpc-gateway-app

CMD ["python", "run.py"]
