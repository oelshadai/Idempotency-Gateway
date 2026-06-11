from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from typing import Optional, Dict, Any


@dataclass
class IdempotencyRecord:
    # hash of request body (used for fraud detection)
    request_hash: str

    # cached response
    response: Optional[Dict[str, Any]] = None

    # HTTP status code of stored response
    status_code: Optional[int] = None

    # tells if request is still being processed
    processing: bool = True

    # used for race condition handling (bonus requirement)
    event: asyncio.Event = field(default_factory=asyncio.Event)

    # for optional cleanup (bonus feature later)
    created_at: datetime = field(default_factory=datetime.utcnow)