import re

def _decamelify(obj):
    def func(string): return re.sub(
        '([a-z0-9])([A-Z])', r'\1_\2', string).lower()
    return modify_object(obj, func)


def _camelify(obj):
    def func(string):
        return re.sub(r'_(\w)', lambda match: match.group(1).upper(), string)
    return modify_object(obj, func)


def modify_object(obj, func):
    if isinstance(obj, dict):
        temp_obj = {}
        for key in obj:
            if isinstance(obj[key], str):
                temp_obj[func(key)] = obj[key]
            else:
                temp_obj[func(key)] = modify_object(obj[key], func)
        return temp_obj
    if isinstance(obj, list):
        temp_obj = []
        for key in obj:
            if isinstance(key, str):
                temp_obj.append(key)
            else:
                temp_obj.append(modify_object(key, func))
        return temp_obj
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, str) and not obj.isupper():
        return func(obj)
    return obj


class Query(object):

    def __init__(self):
        self.query = {}

    def __getattr__(self, name):
        def f(*args, **kw):
            if not getattr(self.query, name, None):
                self.query.setdefault(name, None)
            clean = kw.pop('clean', None)
            if clean:
                self.query[name] = None
            if kw:
                self.query[name] = kw
            elif isinstance(args, list):
                self.query[name] = args
            elif len(args) == 1:
                self.query[name] = args[0]
            return self
        return f

    def json(self, camelify=False):
        if camelify:
            return _camelify(self.query)
        return self.query

    def clone(self, query):
        self.query.update(query.json())
        return self
