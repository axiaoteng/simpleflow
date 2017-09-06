import time
from simpleflow.utils.storage_utils import build_session
from simpleflow.storage.impl import Connection


dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'simpleflow',
       'user': 'root',
       'passwd': '111111'}

session = build_session(dst)

conn = Connection(session)
s = time.time()
for book in conn.get_logbooks():
    print book
print time.time() - s
conn.clear_all()
print time.time() - s