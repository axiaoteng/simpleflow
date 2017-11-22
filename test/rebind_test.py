import collections

import six
from six.moves import zip as compat_zip


from simpleflow.atom import _build_rebind_dict

req_args = ['file', 'timeout']

rebind_args = ['updatefile', 'timeout']

print _build_rebind_dict(req_args, rebind_args)
