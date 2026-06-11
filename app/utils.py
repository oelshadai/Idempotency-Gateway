import hashlib
import json


def hash_payload(payload: dict) -> str:
    """
    Creates a unique fingerprint of request body.
    Used to detect if request data changed.
    """

    normalized = json.dumps(payload, sort_keys=True)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()