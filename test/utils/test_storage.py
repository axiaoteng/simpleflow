from simpleflow.utils import storage_utils as sutil


db_info = {'host': '172.20.0.3',
           'port': 3304,
           'schema': 'simpleflow',
           'user': 'root',
           'passwd': '111111'}

sutil.init_simpleflowdb(db_info)