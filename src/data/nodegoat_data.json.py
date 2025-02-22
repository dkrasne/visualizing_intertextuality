import sys

import json
import os
import requests

# set parameters
api_token = os.getenv("NODEGOAT_API_TOKEN")
project_id = "6081"
scriptdir = os.path.dirname(os.path.abspath(__file__))


######### GET MODEL ##################

# fetch model json from nodegoat
nodegoat_model_url = f"https://nodegoat.io/project/{project_id}/model/type"
headers = {'Authorization': f'Bearer {api_token}', 'Content-Type':'application/json'}

# store the results of requesting the model
r_mod = requests.get(nodegoat_model_url, headers=headers)

# if the GET fails completely or the returned model JSON contains an error statement, load model json and object json from backup
if r_mod.status_code != 200 or "error" in r_mod.json():
    with open(scriptdir+"/model_json_backup.json") as backup_model:
        model_json = json.load(backup_model)
    with open(scriptdir+"/objects_json_backup.json") as backup_file:
        obj_list = json.load(backup_file)
# otherwise proceed
else:
    model_json = r_mod.json()

# function for getting object IDs out of the model
def get_object_ids(model):
    """
    `model` needs to be the JSON of the model fetched from nodegoat
    """
    
    # shortcut to relevant part of model json
    model_types = model["data"]["types"]

    ## I MAY NOT ACTUALLY USE `types_dict`
    # extract the nodegoat IDs for each object type table, plus its name
    # extract list of nodegoat IDs for each object type table
    types_dict = {}
    obj_ids = []
    for key in model_types.keys():
        types_dict[key] = model_types[key]["type"]["name"]
        obj_ids.append(key)
    return obj_ids

obj_ids = get_object_ids(model_json)


######### GET OBJECTS ###############

## ADD ERROR HANDLING FOR A PROBLEMATIC OBJECT CALL FROM API PARTWAY THROUGH
## CHECK WHETHER ANYTHING ELSE NEEDS TO BE CHANGED IF LOADING FROM FILE

# if original API call for model succeeded, do another API call for objects
if 'obj_list' not in locals():

    # fetch all objects from nodegoat
    obj_list = []
    for obj in obj_ids:
        nodegoat_url = f"https://nodegoat.io/project/{project_id}/data/type/{obj}/object"
        obj_r = requests.get(nodegoat_url, headers=headers)
        if obj_r.status_code == 200 and not "error" in obj_r.json():
            obj_list.append(obj_r.json()['data'])
        
        # if API call fails or returns an error at some point, load model and objects from backup
        else:
            with open(scriptdir+"/model_json_backup.json") as backup_model:
                model_json = json.load(backup_model)
            with open(scriptdir+"/objects_json_backup.json") as backup_file:
                obj_list = json.load(backup_file)
            # set the obj_ids to those from the backup model
            obj_ids = get_object_ids(model_json)            

# Assign object types to variables for easy reference, and store in dictionary.
tables_dict = {}
for objtype in obj_list:
    for id_num in objtype["objects"]:
        if objtype["objects"][id_num]["object"]["type_id"] == 21846:
            word_instance_table = objtype["objects"]
            tables_dict["word_instance_table"] = word_instance_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21847:
            word_lvl_intxt_table = objtype["objects"]
            tables_dict["word_lvl_intxt_table"] = word_lvl_intxt_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21853:
            word_lvl_intxt_grp_table = objtype["objects"]
            tables_dict["word_lvl_intxt_grp_table"] = word_lvl_intxt_grp_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21843:
            author_table = objtype["objects"]
            tables_dict["author_table"] = author_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21844:
            work_table = objtype["objects"]
            tables_dict["work_table"] = work_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21854:
            work_seg_table = objtype["objects"]
            tables_dict["work_seg_table"] = work_seg_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21849:
            match_type_class_table = objtype["objects"]
            tables_dict["match_type_class_table"] = match_type_class_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21864:
            lemma_table = objtype["objects"]
            tables_dict["lemma_table"] = lemma_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21879:
            meter_table = objtype["objects"]
            tables_dict["meter_table"] = meter_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21880:
            meter_pos_len_table = objtype["objects"]
            tables_dict["meter_pos_len_table"] = meter_pos_len_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21852:
            position_class_table = objtype["objects"]
            tables_dict["position_class_table"] = position_class_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21856:
            publication_table = objtype["objects"]
            tables_dict["publication_table"] = publication_table
            break
        elif objtype["objects"][id_num]["object"]["type_id"] == 21860:
            pleiades_table = objtype["objects"]
            tables_dict["pleiades_table"] = pleiades_table
            break
        else:
            pass
        # end of inner for loop
    # end of outer for loop


# Write current model and object list to backup files
with open(scriptdir+"/model_json_backup.json", "w") as backup_model:
    json.dump(model_json, backup_model)
with open(scriptdir+"/objects_json_backup.json", "w") as backup_obj_file:
    json.dump(obj_list, backup_obj_file)

# Output final JSON for Framework page
json.dump(tables_dict, sys.stdout)

