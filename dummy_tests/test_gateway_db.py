# test gateway and f7t work together, need to launch both services first
import os
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv

HPCGATEWAY_URL="http://127.0.0.1:5253"

rep = requests.get(urljoin(HPCGATEWAY_URL, 'dbtest'))
print(rep.json(), rep)
