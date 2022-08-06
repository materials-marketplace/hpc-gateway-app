# test gateway and f7t work together, need to launch both services first
import os
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv("../deploy/common.env")

HPCGATEWAY_URL=os.environ.get("HPCGATEWAY_URL")

rep = requests.get(urljoin(HPCGATEWAY_URL, 'broker'))
print(rep.json(), rep)

rep = requests.get(urljoin(HPCGATEWAY_URL, "f7ttest"))
print(rep.json(), rep)