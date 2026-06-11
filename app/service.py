import asyncio
from datetime import datetime

from app.store import idempotency_store
from app.models import IdempotencyRecord
from app.utils import hash_payload

async def process_payment(idempotency_key: str, payload: dict):
    """
    Handles idempotency logic for payment processing.
    """

    request_hash = hash_payload(payload)

    # STEP 1: Check if key exists
    if idempotency_key in idempotency_store:
        record = idempotency_store[idempotency_key]

        # CASE 1: same payload → return cached response
        if record.request_hash == request_hash:

            # BONUS: if still processing → wait
            if record.processing:
                await record.event.wait()

            return {
                "status_code": record.status_code,
                "response": record.response,
                "cache_hit": True
            }

        # CASE 2: same key but different payload → fraud
        return {
            "status_code": 409,
            "error": "Idempotency key already used for a different request body."
        }

    # STEP 2: NEW REQUEST
    event = asyncio.Event()

    record = IdempotencyRecord(
        request_hash=request_hash,
        processing=True,
        event=event
    )

    idempotency_store[idempotency_key] = record

    # STEP 3: simulate payment processing
    await asyncio.sleep(2)

    response = {
        "message": f"Charged {payload['amount']} {payload['currency']}"
    }

    # STEP 4: update record
    record.response = response
    record.status_code = 200
    record.processing = False

    # unblock waiting requests
    record.event.set()

    return {
        "status_code": 200,
        "response": response,
        "cache_hit": False
    }