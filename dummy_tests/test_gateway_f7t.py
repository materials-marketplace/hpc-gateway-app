# test gateway and f7t work together, need to launch both services first
import os
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

HPCGATEWAY_URL = "http://127.0.0.1:5253"

rep = requests.get(urljoin(HPCGATEWAY_URL, "broker"))
print(rep.json(), rep)

rep = requests.get(urljoin(HPCGATEWAY_URL, "f7ttest"))
print(rep.json(), rep)
