from app.models import PaymentRecord

payments = {}
processing = {}
request_bodies = {}


def save_payment(key, record: PaymentRecord):
    payments[key] = record


def get_payment(key):
    return payments.get(key)


def is_processing(key):
    return key in processing


def start_processing(key):
    processing[key] = True


def stop_processing(key):
    processing.pop(key, None)


def store_request_body(key, body):
    request_bodies[key] = body


def get_request_body(key):
    return request_bodies.get(key)