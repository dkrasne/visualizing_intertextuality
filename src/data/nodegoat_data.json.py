import sys

import json
import os
try:
    import requests
except:
    !pip install requests
    import requests


api_token = os.getenv("NODEGOAT_API_TOKEN")
project_id = "6081"

nodegoat_model_url = f"https://nodegoat.io/project/{project_id}/model/type"
headers = {'Authorization': f'Bearer {api_token}', 'Content-Type':'application/json'}

r_mod = requests.get(nodegoat_model_url, headers=headers)
model_json = r_mod.json()

json.dump(model_json, sys.stdout)