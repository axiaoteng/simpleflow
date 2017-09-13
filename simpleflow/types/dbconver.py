"""Converting MySQL and Python types
"""
import sqlite3

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


def SimpleFlowSqliteConverter():
    sqlite3.register_adapter(list, jsonutils.dumps)
    sqlite3.register_adapter(tuple, lambda x: jsonutils.dumps(list(x)))
    sqlite3.register_adapter(set, lambda x: jsonutils.dumps(list(x)))
    sqlite3.register_adapter(dict, jsonutils.dumps)
