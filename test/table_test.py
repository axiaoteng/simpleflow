import sqlalchemy as sa



impl = sa.UnicodeText


def get(dialect):
    return dialect.type_descriptor(impl)