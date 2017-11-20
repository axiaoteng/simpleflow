import collections

import six
from six.moves import zip as compat_zip


from simpleflow.atom import _build_rebind_dict

req_args = ['timeout', 'file']

rebind_args = ['download_timeout']

print _build_rebind_dict(req_args, rebind_args)
