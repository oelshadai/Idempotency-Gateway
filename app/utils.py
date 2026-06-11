import hashlib
import json


def hash_request(data):
    return hashlib.md5(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()