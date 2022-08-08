import json
import requests
import os
from urllib.parse import urljoin
import logging
import threading
from logging.handlers import TimedRotatingFileHandler

from marketplace_standard_app_api.models.message_broker import (
    MessageBrokerRequestModel,
    MessageBrokerResponseModel,
)

from marketplace.message_broker.rpc_server import RpcServer


HPCGATEWAY_URL = os.environ.get("HPCGATEWAY_URL")

# formatter is executed for every log
class LogRequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.TID = threading.current_thread().name
        except:
            record.TID = 'notid'

        return super().format(record)

def relay(request: MessageBrokerRequestModel):
    """get request from broker, process the request so hpc app can understand it.
    then relay it to hpc app then return (resp, status_code)
    """
    try:
        token = request.headers["authorization"].split(" ")[1]
        # print(token)
    except:
        return {
            "message": "Authentication Token is missing from broker's request!",
            "data": None,
            "error": "Unauthorized"
        }, 401
        
    headers = {
        "Accept": "application/json",
        "User-Agent": "RPC broker",
        "Authorization": f"Bearer {token}",
    }
    
    endpoint = request.endpoint
    
    logging.info(f"RPC relaying endpoint {endpoint} ....")
    # endpoint = '/broker'    # test
    abs_url = urljoin(HPCGATEWAY_URL, endpoint)

    # Use GET request method
    # TODO how I know it is GET??
    params = request.query_params
    if endpoint == '' or endpoint == 'jobs/' or 'download/' in endpoint:
        resp = requests.get(
            abs_url,
            params=params,
            headers=headers,
            verify=None,
        )
    elif endpoint == 'jobs/new/' or 'jobs/run/' in endpoint:
        resp = requests.post(
            abs_url,
            params=params,
            headers=headers,
            verify=None,
        )
    elif 'upload/' in endpoint:
        resp = requests.put(
            abs_url,
            params=params,
            headers=headers,
            verify=None,
        )
    else:
        # DELETE
        resp = requests.delete(
            abs_url,
            params=params,
            headers=headers,
            verify=None,
        )
    
    return resp.json(), resp.status_code

def hpc_message_relayer(
    request_message: MessageBrokerRequestModel,
) -> MessageBrokerResponseModel:
    
    response, status_code = relay(request_message)
    # print(request_message)
    
    response_message = MessageBrokerResponseModel(
        status_code=status_code,
        body=json.dumps(response),
        headers={"Content-Type": "application/json"},
    )
    return response_message

if __name__ == '__main__':
    LOG_PATH = os.environ.get("BROKER_LOG_PATH", "./deploy/logs/broker")
    # timed rotation: 1 (interval) rotation per day (when="D")
    logHandler = TimedRotatingFileHandler(f'{LOG_PATH}/rpc-server.log', when='D', interval=1)

    logFormatter = LogRequestFormatter('%(asctime)s,%(msecs)d %(thread)s [%(TID)s] %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                                    '%Y-%m-%dT%H:%M:%S')
    logHandler.setFormatter(logFormatter)

    # get app log (python)
    logger = logging.getLogger()
    
    logging.info("RPC SERVER IS RUNNING....")

    # set handler to logger
    logger.addHandler(logHandler)
    logging.getLogger().setLevel(logging.DEBUG)
    
    # disable Flask internal logging to avoid full url exposure
    logging.getLogger('pika').propagate = False
    
    gateway_client_id = os.environ.get('GATEWAY_CLIENT_ID')
    gateway_client_secret = os.environ.get('GATEWAY_CLIENT_SECRET')
    host = os.environ.get("MP_HOST_URL")
    
    rpc_server = RpcServer(
        host=host,
        application_id=gateway_client_id,
        application_secret=gateway_client_secret,
        message_handler=hpc_message_relayer,
    )
    rpc_server.consume_messages()