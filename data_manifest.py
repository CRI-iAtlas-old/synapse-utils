import synapseclient
import synapseutils as su
import pandas as pd

def _check_filename(syn, synId):
    entity = syn.getEntity(synId)
    if entity['_file_handle']['fileName'] == 'NOT_SET':
        return os.path.basename(entity['_file_handle']['externalURL'])

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
