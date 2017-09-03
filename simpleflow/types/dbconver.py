"""Converting MySQL and Python types
"""

from simpleutil.utils import jsonutils

from mysql.connector.conversion import MySQLConverter


class SimpleFlowConverter(MySQLConverter):

    def _dict_to_mysql(self, value):
        return jsonutils.dumps(value)
