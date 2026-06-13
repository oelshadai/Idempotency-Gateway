from flask import Blueprint, request, jsonify
from datetime import datetime

from app.service import process_payment
from app.utils import hash_request
from app.models import PaymentRecord

from app.store import (
    is_processing,
    start_processing,
    stop_processing,
    wait_for_processing,
    get_payment,
    save_payment,
    store_request_body,
    get_request_body
)

payment_bp = Blueprint("payments", __name__)


@payment_bp.route("/process-payment", methods=["POST"])
def handle_payment():
    """
    Process a payment using an Idempotency-Key
    ---
    tags:
      - Payments
    consumes:
      - application/json
    parameters:
      - in: header
        name: Idempotency-Key
        type: string
        required: true
        description: Unique key identifying this payment request
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
            - currency
          properties:
            amount:
              type: number
              example: 100
            currency:
              type: string
              example: GHS
    responses:
      200:
        description: Payment processed successfully (or cached response returned for duplicate request)
        headers:
          X-Cache-Hit:
            type: string
            description: "Present and set to 'true' when returning a cached/duplicate response"
        examples:
          application/json:
            status: success
            message: "Charged 100 GHS"
      400:
        description: Missing Idempotency-Key header
        examples:
          application/json:
            error: "Idempotency-Key required"
      409:
        description: Idempotency key reused with a different request body
        examples:
          application/json:
            error: "Idempotency key already used for a different request body."
    """

    data = request.get_json()
    key = request.headers.get("Idempotency-Key")

    if not key:
        return jsonify({"error": "Idempotency-Key required"}), 400

    request_hash = hash_request(data)

    # 1. Cached response (idempotency replay)
    existing = get_payment(key)
    if existing:
        return jsonify(existing.response), 200, {"X-Cache-Hit": "true"}

    # 2. Conflict detection (same key, different payload)
    previous_body = get_request_body(key)
    if previous_body and previous_body != data:
        return jsonify({
            "error": "Idempotency key already used for a different request body."
        }), 409

    # 3. In-flight protection (BONUS FIXED)
    if is_processing(key):
        wait_for_processing(key)

        existing = get_payment(key)
        if existing:
            return jsonify(existing.response), 200, {"X-Cache-Hit": "true"}

    # 4. Start processing
    start_processing(key)

    try:
        store_request_body(key, data)

        response = process_payment(
            amount=data.get("amount"),
            currency=data.get("currency")
        )

        record = PaymentRecord(
            idempotency_key=key,
            request_hash=request_hash,
            amount=data.get("amount"),
            currency=data.get("currency"),
            response=response,
            status="success",
            created_at=datetime.utcnow()
        )

        save_payment(key, record)

        return jsonify(response), 200

    finally:
        stop_processing(key)