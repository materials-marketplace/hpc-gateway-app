# test that f7t server running fine
import os
import firecrest as f7t
from dotenv import load_dotenv

load_dotenv("../deploy/common.env")

# Configuration parameters for the Authorization Object
F7T_TOKEN = os.environ.get("F7T_TOKEN")
F7T_URL = os.environ.get("F7T_URL")

# Create an authorization object with Client Credentials authorization grant
class HardCodeTokenAuth:
    
    def __init__(self, token):
        self._token = token
        
    def get_access_token(self):
        return self._token
    
hardcode = HardCodeTokenAuth(
    token=F7T_TOKEN,
)

# Setup the client for the specific account
client = f7t.Firecrest(
    firecrest_url=F7T_URL, 
    authorization=hardcode,
)

try:
    parameters = client.parameters()
    print(f"Firecrest parameters: {parameters}")
    print(client.list_files(machine='cluster', target_path='/home/jyu'))
    # print(client.mkdir(machine='cluster', target_path='/home/jyu/thmoo'))
    print(client.poll(machine='cluster'))
except f7t.FirecrestException as e:
    # When the error comes from the responses to a firecrest request you will get a
    # `FirecrestException` and from this you can examine the http responses yourself
    # through the `responses` property
    print(e)
    print(e.responses)
except Exception as e:
    # You might also get regular exceptions in some cases. For example when you are
    # trying to upload a file that doesn't exist in your local filesystem.
    print(e)