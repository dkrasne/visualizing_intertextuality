import sys

import json
import os
import requests
import pandas as pd

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

########## PREPARE OBJECT DATA FOR MANIPULATION #######

# Create table dataframes
def table_to_df(table, cols_dict):
    dictlist = []
    for id in table:
        tdict = {}
        obj_defs = table[id]["object_definitions"]
        tdict["obj_id"] = id
        for key, val in cols_dict.items():
            # key becomes key in tdict
            id_val = list(val.keys())[0]
            if val[id_val] == "refid":
                try:
                    tdict[str(key)] = obj_defs[str(id_val)]["object_definition_ref_object_id"]
                except:
                    tdict[str(key)] = None
            elif val[id_val] == "objval":
                try:
                    tdict[str(key)] = obj_defs[str(id_val)]["object_definition_value"]
                except:
                    tdict[str(key)] = None
        dictlist.append(tdict)
    df = pd.DataFrame.from_dict(dictlist)
    for col in df:
        if col[-3:] == "_id":
            df[col] = df[col].astype(str)
    return df

# Prepare columns for dataframes
wd_inst_cols = {"word": {"67388": "objval"},
                "lemma_id": {"67389": "refid"},
                "work_segment_id": {"67390": "refid"},
                "line_num": {"67405": "objval"},
                "line_num_modifier": {"67411": "objval"},
                "start_pos_id": {"67401": "refid"},
                #"start_pos": {"67401": "objval"},
                "end_pos_id": {"67402": "refid"},
                #"end_pos": {"67402": "objval"}
                }
wd_lvl_intxt_cols = {"source_word_id": {"67392": "refid"},
                     "target_word_id": {"67393": "refid"},
                     "match_type_ids": {"67397": "refid"}}
wd_lvl_intxt_grp_cols = {"word_intxt_ids": {"67406": "refid"}}
author_cols = {"author_name": {"67375": "objval"},
               "wikidata_url": {"67383": "objval"},
               "praenomen": {"67385": "objval"},
               "nomen": {"67386": "objval"},
               "cognomen": {"67387": "objval"}}
work_cols = {"title": {"67378": "objval"},
             "author_id": {"67379": "refid"},
             "cts_urn": {"67533": "objval"}}
work_seg_cols = {"work_id": {"67408": "refid"},
                 "work_section": {"67410": "objval"},
                 "work_subsection": {"67539": "objval"},
                 "follows_id": {"67525": "refid"},
                 "meter_id": {"67531": "refid"},
                 "perseus_url": {"67534": "objval"}}
lemma_cols = {"lemma": {"67440": "objval"},
              "lila_uri": {"67441": "objval"}}
meter_cols = {"meter_name": {"67527": "objval"},
              "max_line_beats": {"67528": "objval"},
              "recur_line_pattern": {"67529": "objval"},
              "ok_word_pos": {"67530": "refid"}}
meter_pos_len_cols = {"meter_id": {"67535": "refid"},
                      "position_id": {"67536": "refid"},
                      "max_length": {"67537": "objval"}}

# Convert tables to dataframes based on specified columns
word_instance_df = table_to_df(word_instance_table, wd_inst_cols)
word_lvl_intxt_df = table_to_df(word_lvl_intxt_table, wd_lvl_intxt_cols)
word_lvl_intxt_grp_df = table_to_df(word_lvl_intxt_grp_table, wd_lvl_intxt_grp_cols)
author_df = table_to_df(author_table, author_cols)
work_df = table_to_df(work_table,work_cols)
work_seg_df = table_to_df(work_seg_table,work_seg_cols)
lemma_df = table_to_df(lemma_table,lemma_cols)
meter_df = table_to_df(meter_table,meter_cols)
meter_pos_len_df = table_to_df(meter_pos_len_table,meter_pos_len_cols)

# Convert tables to dataframes for classification/lookup tables
match_type_class_list = []
for mt in match_type_class_table:
    mt_dict = {}
    mt_dict["match_type_id"] = mt
    mt_dict["match_type"] = match_type_class_table[mt]["object"]["object_name"]
    match_type_class_list.append(mt_dict)
match_type_class_df = pd.DataFrame.from_dict(match_type_class_list)

position_class_list = []
for pt in position_class_table:
    pt_dict = {}
    pt_dict["position_id"] = pt
    pt_dict["position"] = position_class_table[pt]["object"]["object_name"]
    position_class_list.append(pt_dict)
position_class_df = pd.DataFrame.from_dict(position_class_list)

############ Join tables and make JSON objects###########

# Meter, position, length
meter_df.index = meter_df.obj_id
meter_df_ext = pd.merge(pd.merge(meter_df.drop("obj_id", axis=1), 
                                 meter_pos_len_df, how="left", left_index=True, right_on="meter_id"), 
                                 position_class_df, how="left", left_on="position_id", right_on="position_id").rename(columns={"obj_id": "meter_pos_len_id"})

meters_dict = {}
meter_names = list(meter_df_ext["meter_name"].unique())
for meter in meter_names:
    meter_dict = {}
    meter_pos_len_list = []
    meter_df_ext_sub = meter_df_ext.query(f"meter_name == '{meter}'").sort_values("position").reset_index()
    for i in range(len(meter_df_ext_sub)):
        pos_dict = {}
        pos_dict["position"] = meter_df_ext_sub.loc[i, "position"]
        pos_dict["pos_len"] = int(meter_df_ext_sub.loc[i, "max_length"])
        pos_dict["meter_pos_len_id"] = meter_df_ext_sub.loc[i, "meter_pos_len_id"]
        meter_pos_len_list.append(pos_dict)
    meter_dict["meter_id"] = meter_df_ext_sub["meter_id"].unique()[0]
    meter_dict["max_line_beats"] = int(meter_df_ext_sub["max_line_beats"].unique()[0])
    meter_dict["recur_line_pattern"] = int(meter_df_ext_sub["recur_line_pattern"].unique()[0])
    meter_dict['positions'] = meter_pos_len_list
    meters_dict[meter] = meter_dict

# write meters dictionary to JSON file
with open(scriptdir+"/meters.json", "w") as meters_json:
    json.dump(meters_dict, meters_json)



# Write current model and object list to backup files
with open(scriptdir+"/model_json_backup.json", "w") as backup_model:
    json.dump(model_json, backup_model)
with open(scriptdir+"/objects_json_backup.json", "w") as backup_obj_file:
    json.dump(obj_list, backup_obj_file)

# Output final JSON for Framework page
json.dump(tables_dict, sys.stdout)

