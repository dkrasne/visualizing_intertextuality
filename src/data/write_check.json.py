import sys
import os
import json

scriptdir = os.path.dirname(os.path.abspath(__file__))



if os.access(scriptdir+"/model_json_backup.json", os.W_OK):
    var = "yes"
else:
    var = "no"
sys.stdout.write('{"answer":"'+var+'"}')