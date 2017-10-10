import os

import synapseclient
import synapseutils as su
import pandas as pd


def _expand_fileinfo(syn, synId):
    #print("_expand_fileinfo `syn`: {}".format(syn))
    #print("_expand_fileinfo `synId`: {}".format(synId))
    entity = syn.getEntity(synId)
    fileinfo_fields = ['createdBy', 'modifiedBy', 'versionNumber']
    fileinfo = {k: v for k, v in entity.items()
                if k in fileinfo_fields}
   
    entity_filehandle = entity['_file_handle']
    filehandleinfo_fields = ['contentMd5', 'contentSize',
                             'externalURL', 'fileName']
    filehandleinfo = {k: v for k, v in entity_filehandle.items()
                      if k in filehandleinfo_fields}
    if filehandleinfo['fileName'] == 'NOT_SET':
        filehandleinfo['downloadName'] = os.path.basename(
            filehandleinfo['externalURL']
        )
    else:
        filehandleinfo['downloadName'] = filehandleinfo['fileName']

    return {**fileinfo, **filehandleinfo}


def add_fileinfo(syn, df):
    #print("add_fileinfo `syn`: {}".format(syn))
    #print("add_fileinfo `df`: {}".format(df))
    fileinfo = _expand_fileinfo(syn, df['fileId'])
    for k in fileinfo:
        df[k] = fileinfo[k]
    return df


def _expand_userinfo(syn, userId):
    userinfo = syn.getUserProfile(userId)
    return {'User': userinfo['userName'],
            'Name': ' '.join([userinfo['firstName'], userinfo['lastName']])}
 

def add_userinfo(syn, df, usercol):
    userinfo = _expand_userinfo(syn, df[usercol])
    for k in userinfo:
        addcol = usercol + k
        df[addcol] = userinfo[k]
    return df


def synwalk_to_df(syn, synId):
    res = []
    for root, dirs, files in su.walk(syn, synId):
        if len(files) > 0:
            path_names = [root[0]]*len(files)
            path_ids = [root[1]]*len(files)
            file_names = map(lambda x: x[0], files)
            file_ids = map(lambda x: x[1], files)
            res.extend(zip(path_names, path_ids, file_names, file_ids))
    return pd.DataFrame(res, columns=['folderPath', 'folderId', 'fileName', 'fileId'])


def build_manifest(syn, synId):
    base_df = synwalk_to_df(syn, synId)
    manifest_df = (
        base_df
        .apply(lambda x: add_fileinfo(syn, x), axis=1)
        .apply(lambda x: add_userinfo(syn, x, 'createdBy'), axis=1)
        .apply(lambda x: add_userinfo(syn, x, 'modifiedBy'), axis=1)
        .rename(columns={'createdBy': 'createdById', 
                         'modifiedBy': 'modifiedById'})
    )
    return manifest_df
