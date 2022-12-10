import logging
import os
import threading
from logging.handlers import TimedRotatingFileHandler
from urllib.parse import urljoin

import requests
from marketplace.message_broker.rpc_server import RpcServer
from marketplace_standard_app_api.models.message_broker import (
    MessageBrokerRequestModel,
    MessageBrokerResponseModel,
)

HPCGATEWAY_URL = os.environ.get("HPCGATEWAY_URL")
GATEWAY_CLIEND_ID = os.environ.get("GATEWAY_CLIENT_ID")
GATEWAY_CLIEND_SECRET = os.environ.get("GATEWAY_CLIENT_SECRET")
MP_HOST_URL = os.environ.get("MP_HOST_URL")
LOG_PATH = os.environ.get("BROKER_LOG_PATH", "./deploy/logs/broker")


# formatter is executed for every log
class LogRequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.TID = threading.current_thread().name
        except Exception:
            record.TID = "notid"

        return super().format(record)


def hpc_message_relayer(
    request_message: MessageBrokerRequestModel,
) -> MessageBrokerResponseModel:
    """get request from broker, process the request so hpc app can understand it.
    then relay it to hpc app then return.
    """
    endpoint = request_message.endpoint

    logging.info(f"RPC relaying endpoint {endpoint} ....")
    abs_url = urljoin(HPCGATEWAY_URL, endpoint)

    try:
        resp = requests.request(
            request_message.method,
            url=abs_url,
            params=request_message.query_params,
            headers=request_message.headers,
            data=request_message.body,
        )
        
        response_message = MessageBrokerResponseModel(
            status_code=resp.status_code,
            body=resp.content,
            headers=resp.headers,
        )
    except Exception as e:
        print(e)
        return {
            "error": f"Error: You request to {endpoint} failed with {str(e)}",
        }, 400
        response_message = MessageBrokerResponseModel(
            status_code=400,
            body='{\n  "message": "HPC-gateway-App : app fail."\n}\n',
            headers="{'Content-Type': 'application/json', 'Connection': 'close'}",
        )    
    
    return response_message

if __name__ == "__main__":
    # timed rotation: 1 (interval) rotation per day (when="D")
    logHandler = TimedRotatingFileHandler(
        f"{LOG_PATH}/rpc-server.log", when="D", interval=1
    )

    logFormatter = LogRequestFormatter(
        "%(asctime)s,%(msecs)d %(thread)s [%(TID)s] %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        "%Y-%m-%dT%H:%M:%S",
    )
    logHandler.setFormatter(logFormatter)

    # get app log (python)
    logger = logging.getLogger()

    logging.info("RPC SERVER IS RUNNING....")

    # set handler to logger
    logger.addHandler(logHandler)
    logging.getLogger().setLevel(logging.DEBUG)

    # disable Flask internal logging to avoid full url exposure
    logging.getLogger("pika").propagate = False

    gateway_client_id = GATEWAY_CLIEND_ID
    gateway_client_secret = GATEWAY_CLIEND_SECRET
    host = MP_HOST_URL

    rpc_server = RpcServer(
        host=host,
        application_id=gateway_client_id,
        application_secret=gateway_client_secret,
        message_handler=hpc_message_relayer,
    )
    rpc_server.consume_messages()
