from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaymentRecord:
    idempotency_key: str
    request_hash: str
    amount: float
    currency: str
    response: dict
    status: str
    created_at: datetime