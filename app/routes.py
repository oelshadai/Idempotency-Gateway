from flask import Blueprint, request, jsonify
from app.store import payments, processing, request_bodies
from app.utils import hash_request
from app.service import process_payment
import time

payment_bp = Blueprint("payments", __name__)


@payment_bp.route("/process-payment", methods=["POST"])
def handle_payment():
    data = request.get_json()
    key = request.headers.get("Idempotency-Key")

    if not key:
        return jsonify({"error": "Idempotency-Key required"}), 400

    # CASE 1: already completed request
    if key in payments:
        return jsonify(payments[key]), 200, {"X-Cache-Hit": "true"}

    # CASE 2: conflict (same key, different payload)
    if key in request_bodies and request_bodies[key] != data:
        return jsonify({
            "error": "Idempotency key already used for a different request body."
        }), 409

    # CASE 3: in-flight request (race condition handling)
    while key in processing:
        time.sleep(0.1)

    processing[key] = True

    try:
        # store original request body
        request_bodies[key] = data

        response = process_payment(
            amount=data.get("amount"),
            currency=data.get("currency")
        )

        payments[key] = response
        return jsonify(response), 200

    finally:
        processing.pop(key, None)