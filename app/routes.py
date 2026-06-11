from flask import Blueprint, request, jsonify
from datetime import datetime

from app.service import process_payment
from app.utils import hash_request
from app.models import PaymentRecord

from app.store import (
    is_processing,
    start_processing,
    stop_processing,
    get_payment,
    save_payment,
    store_request_body,
    get_request_body
)

payment_bp = Blueprint("payments", __name__)


@payment_bp.route("/process-payment", methods=["POST"])
def handle_payment():
    """
    Process Payment Endpoint
    ---
    tags:
      - Payments
    description: Processes a payment with idempotency protection
    parameters:
      - name: Idempotency-Key
        in: header
        type: string
        required: true
        description: Unique key to prevent duplicate payments

      - name: body
        in: body
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
        description: Successful or cached payment response
      400:
        description: Missing Idempotency-Key
      409:
        description: Idempotency key used with different payload
    """

    data = request.get_json()
    key = request.headers.get("Idempotency-Key")

    if not key:
        return jsonify({"error": "Idempotency-Key required"}), 400

    request_hash = hash_request(data)

    # 1. Return cached response
    existing = get_payment(key)
    if existing:
        return jsonify(existing.response), 200, {"X-Cache-Hit": "true"}

    # 2. Conflict detection
    previous_body = get_request_body(key)
    if previous_body and previous_body != data:
        return jsonify({
            "error": "Idempotency key already used for a different request body."
        }), 409

    # 3. In-flight protection (race condition handling)
    while is_processing(key):
        pass

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