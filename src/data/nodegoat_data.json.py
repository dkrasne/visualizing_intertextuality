import sys

import json
import os
import requests
import pandas as pd
import networkx as nx

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
### I think I've done this now?

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

    # convert numeric IDs to string and remove any trailing decimals
    for col in df:
        if col[-3:] == "_id":
            df[col] = df[col].astype(str)
    def remove_decimal(id_string):
        if isinstance(id_string, str) and id_string[-2:] == ".0":
            return id_string[:-2]
        return id_string
    for col in df:
        if col[-3:] == "_id":
            df[col] = df[col].apply(remove_decimal)

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
               "language": {"68096": "objval"},
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
                 "first_line": {"68041": "objval"},
                 "last_line": {"68042": "objval"},
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
                      "max_length": {"67537": "objval"},
                      "unit_line": {"68127": "objval"}}

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

# Meter + position + length extended dataframe
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
        pos_dict["pos_len"] = int(meter_df_ext_sub.loc[i, "max_length"]) # use int() to convert from np.int64
        pos_dict["meter_pos_len_id"] = meter_df_ext_sub.loc[i, "meter_pos_len_id"]
        pos_dict["unit_line"] = int(meter_df_ext_sub.loc[i, "unit_line"]) # use int() to convert from np.int64
        meter_pos_len_list.append(pos_dict)
    meter_dict["meter_id"] = meter_df_ext_sub["meter_id"].unique()[0]
    meter_dict["max_line_beats"] = int(meter_df_ext_sub["max_line_beats"].unique()[0]) # use int() to convert from np.int64
    meter_dict["recur_line_pattern"] = int(meter_df_ext_sub["recur_line_pattern"].unique()[0]) # use int() to convert from np.int64
    meter_dict['positions'] = meter_pos_len_list
    meters_dict[meter] = meter_dict

# write meters dictionary to JSON file
with open(scriptdir+"/meters.json", "w") as meters_json:
    json.dump(meters_dict, meters_json)


# Word + Lemma + Work + Work Segment + Author



######## OUTPUT ALL DATAFRAMES IN DICT -> JSON FORMAT ############

tables_list = ['word_instance_table',
 'word_lvl_intxt_table',
 'word_lvl_intxt_grp_table',
 'author_table',
 'work_table',
 'work_seg_table',
 'lemma_table',
 'meter_table',
 'meter_pos_len_table',
 'match_type_class_table']

df_list = [word_instance_df,
           word_lvl_intxt_df,
           word_lvl_intxt_grp_df,
           author_df,
           work_df,
           work_seg_df,
           lemma_df,
           meter_df,
           meter_pos_len_df,
           match_type_class_df]

tables_df_to_dict = {}

for i, df in enumerate(df_list):
    df_name = tables_list[i]
    new_dict = df.to_dict(orient='records')
    tables_df_to_dict[df_name] = new_dict

with open(scriptdir+"/nodegoat_tables.json", "w") as table_json:
    json.dump(tables_df_to_dict, table_json)


######## CREATE NETWORK ##############

# In preparation for creating a network, create a full set of intertexts, starting at the group level, with IDs for all features

grp_intxts_list = [str(item) for sublist in list(word_lvl_intxt_grp_df.word_intxt_ids) for item in sublist]
intxt_grp_list = []

def build_intxt_dict(intxt_ids):
    for intxt in intxt_ids:
        intxt_id = str(intxt)
        for row2 in word_lvl_intxt_df[word_lvl_intxt_df.obj_id == intxt_id].iterrows():
            row_dict = {}
            if intxt_id in grp_intxts_list:
                row_dict["intxt_grp_id"] = intxt_grp_id
            else:
                row_dict["intxt_grp_id"] = None
            row_dict["intxt_id"] = intxt_id
            row2 = row2[1]
            source_id = row2.source_word_id
            target_id = row2.target_word_id
            if isinstance(row2.match_type_ids, list):
                match_type_ids = [str(id) for id in row2.match_type_ids]
            else:
                match_type_ids = []
            row_dict["source_word_id"] = source_id
            row_dict["target_word_id"] = target_id
            source_df = word_instance_df.copy().query(f"obj_id == '{source_id}'").reset_index(drop=True) \
                .merge(work_seg_df, how="left", left_on="work_segment_id", right_on="obj_id").drop("obj_id_y", axis=1) \
                .merge(work_df, how="left", left_on="work_id", right_on="obj_id")[['obj_id_x','word','work_segment_id', 'line_num','line_num_modifier',"work_id","author_id"]]
            target_df = word_instance_df.copy().query(f"obj_id == '{target_id}'").reset_index(drop=True) \
                .merge(work_seg_df, how="left", left_on="work_segment_id", right_on="obj_id").drop("obj_id_y", axis=1) \
                .merge(work_df, how="left", left_on="work_id", right_on="obj_id")[['obj_id_x','word','work_segment_id', 'line_num','line_num_modifier',"work_id","author_id"]]
            row_dict["source_author_id"] = source_df.loc[0,'author_id']
            row_dict["source_work_id"] = source_df.loc[0,'work_id']
            row_dict["source_work_seg_id"] = source_df.loc[0,'work_segment_id']
            if isinstance(source_df.loc[0,'line_num_modifier'], str):
                row_dict["source_line_num"] = str(source_df.loc[0,'line_num'])+source_df.loc[0,'line_num_modifier']
            else:
                row_dict["source_line_num"] = str(source_df.loc[0,'line_num'])
            row_dict["target_author_id"] = target_df.loc[0,'author_id']
            row_dict["target_work_id"] = target_df.loc[0,'work_id']
            row_dict["target_work_seg_id"] = target_df.loc[0,'work_segment_id']
            if isinstance(target_df.loc[0,'line_num_modifier'],str):
                row_dict["target_line_num"] = str(target_df.loc[0,'line_num'])+target_df.loc[0,'line_num_modifier']
            else:
                row_dict["target_line_num"] = str(target_df.loc[0,'line_num'])
            row_dict["match_type_ids"] = match_type_ids
            intxt_grp_list.append(row_dict)

for row in word_lvl_intxt_grp_df.iterrows():
    row = row[1]
    intxt_grp_id = row.obj_id
    intxt_ids = row.word_intxt_ids
    build_intxt_dict(intxt_ids)
build_intxt_dict([intxt for intxt in word_lvl_intxt_df.obj_id if intxt not in grp_intxts_list])

intxt_full_df = pd.DataFrame.from_dict(intxt_grp_list)

with open(scriptdir+"/intxts_full.json", "w") as intxts_full:
    json.dump(intxt_grp_list, intxts_full)


######### CREATE AND EXPORT NETWORK ####################

G = nx.MultiDiGraph()

def add_intxt_multi(sub_df, id, graph):
    # each node is a work_segment_id for a given intertext; author and work IDs are attributes
    source = sub_df.loc[0,"source_work_seg_id"]
    target = sub_df.loc[0,"target_work_seg_id"]
    source_author = sub_df.loc[0,"source_author_id"]
    source_work = sub_df.loc[0,"source_work_id"]
    target_author = sub_df.loc[0,"target_author_id"]
    target_work = sub_df.loc[0,"target_work_id"]
    # the words included in each intertext group are attached to the source or target node (as appropriate) with the group ID or intertext ID as the key
    source_words = list(sub_df.source_word_id.unique())
    target_words = list(sub_df.target_word_id.unique())
    # the edge is identified by the group ID or intertext ID (for any intertexts not included in a group)
    edge = id
    edge_weight = (len(source_words) + len(target_words))/2
    # the match types are added as an attribute to the edge
    if len(sub_df) > 1:
        match_types = list(set(sub_df.match_type_ids.sum()))
    else:
        match_types = list(sub_df.loc[0,"match_type_ids"])
    if not graph.has_node(source):
        graph.add_node(source, author=source_author, work=source_work, id=source_words)
    else:
        nx.set_node_attributes(graph, values={source: source_words}, name=id)
    if not graph.has_node(target):
        graph.add_node(target, author=target_author, work=target_work, id=target_words)
    else:
        nx.set_node_attributes(graph, values={target: target_words}, name=id)
    graph.add_edge(source, target, key=edge, match_types=match_types, weight=edge_weight)

for id in intxt_full_df.intxt_grp_id.unique():
    if isinstance(id, str):
        sub_df = intxt_full_df.query(f"intxt_grp_id == '{id}'").reset_index(drop=True)
        add_intxt_multi(sub_df, id, G)
for id in intxt_full_df[intxt_full_df.intxt_grp_id.isna()].intxt_id:
    sub_df = intxt_full_df.query(f"intxt_id == '{id}'").reset_index(drop=True)
    add_intxt_multi(sub_df, id, G)

graph_json = nx.node_link_data(G)

with open(scriptdir+"/intxt_network_graph.json", "w") as graph_file:
    json.dump(graph_json, graph_file)

######## CREATE AND EXPORT DATA FOR SANKEY DIAGRAM ###############

def prep_sankey(df):
    nodes_edges_dict = {}
    grp_df = df[~df.intxt_grp_id.isna()]
    no_grp_df = df[df.intxt_grp_id.isna()].drop("intxt_grp_id", axis=1)
    grp_ids = list(grp_df.intxt_grp_id.unique())
    no_grp_ids = list(no_grp_df.intxt_id.unique())
    nodes = []
    edges = []
    for work_seg in list(df.source_work_seg_id.unique()):
        author = df[df.source_work_seg_id == work_seg].reset_index(drop=True).loc[0,"source_author_id"]
        work = df[df.source_work_seg_id == work_seg].reset_index(drop=True).loc[0,"source_work_id"]
        nodes.append({"name": work_seg, "author": author, "work": work})
    # print(len(nodes))
    for work_seg in list(df.target_work_seg_id.unique()):
        if work_seg not in [item["name"] for item in nodes]:
            author = df[df.target_work_seg_id == work_seg].reset_index(drop=True).loc[0,"target_author_id"]
            work = df[df.target_work_seg_id == work_seg].reset_index(drop=True).loc[0,"target_work_id"]
            nodes.append({"name": work_seg, "author": author, "work": work})
    # print(len(nodes))
    # print(nodes)
    nodes_edges_dict["nodes"] = nodes
    def make_edge(id, df, grp=True):
        source = df.loc[0, "source_work_seg_id"]
        target = df.loc[0, "target_work_seg_id"]
        source_words = list(df.source_word_id.unique())
        target_words = list(df.target_word_id.unique())
        num_words = (len(source_words)+len(target_words))/2    # using average because sometimes multiple words are compressed into a single word or a single word is split into multiple words
        id = id
        if grp == True:
            group_id = True
        else:
            group_id = False
        edge_dict = {"source": source,
                     "target": target,
                     "source_words": source_words,
                     "target_words": target_words,
                     "num_words": num_words,
                     "id": id,
                     "group_id": group_id}
        return edge_dict
    for id in grp_ids:
        sub_df = grp_df.query(f"intxt_grp_id == '{id}'").reset_index(drop=True)
        edges.append(make_edge(id, sub_df))
    for id in no_grp_ids:
        sub_df = no_grp_df.query(f"intxt_id == '{id}'").reset_index(drop=True)
        edges.append(make_edge(id, sub_df, grp=False))
    # print(edges)
    nodes_edges_dict["edges"] = edges
    return nodes_edges_dict

sankey_data = prep_sankey(intxt_full_df)

with open(scriptdir+"/sankey_data.json", "w") as sankey_file:
    json.dump(sankey_data, sankey_file)

########## BACKUP AND OUTPUT NODEGOAT MODEL AND OBJECT DATA ##############

# Write current model and object list to backup files
with open(scriptdir+"/model_json_backup.json", "w") as backup_model:
    json.dump(model_json, backup_model)
with open(scriptdir+"/objects_json_backup.json", "w") as backup_obj_file:
    json.dump(obj_list, backup_obj_file)

# Output final JSON for Framework page
json.dump(tables_dict, sys.stdout)

