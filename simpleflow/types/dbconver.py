"""Converting MySQL and Python types
"""

from simpleutil.utils import jsonutils

from mysql.connector.conversion import MySQLConverter


class SimpleFlowConverter(MySQLConverter):

    def _dict_to_mysql(self, value):
        return jsonutils.dumps(value)

    def _list_to_mysql(self, value):
        return jsonutils.dumps(value)

    def _tuple_to_mysql(self, value):
        return jsonutils.dumps(list(value))

    def _set_to_mysql(self, value):
        return jsonutils.dumps(list(value))
