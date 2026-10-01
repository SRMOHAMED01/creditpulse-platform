"""Local compatibility shim for the Windows environment.

The project venv currently contains a ujson binary that is blocked by local
Application Control policy. FastAPI only needs the basic JSON helpers here, so
we provide a pure-Python fallback to keep the app importable in this environment.
"""

import json


def dumps(obj, *args, **kwargs):
    return json.dumps(obj, *args, **kwargs)


def loads(value, *args, **kwargs):
    return json.loads(value, *args, **kwargs)


__version__ = "0.0.0-shim"
