from app.models import PaymentRecord
import threading

payments = {}
processing = {}
request_bodies = {}
locks = {}  # used for in-flight waiting (Event per idempotency key)


def save_payment(key, record: PaymentRecord):
    payments[key] = record


def get_payment(key):
    return payments.get(key)


def is_processing(key):
    return processing.get(key, False)


def start_processing(key):
    processing[key] = True

    # create an event for this key if not exists
    locks[key] = threading.Event()


def wait_for_processing(key):
    event = locks.get(key)
    if event:
        event.wait()  # block until processing finishes


def stop_processing(key):
    processing.pop(key, None)

    event = locks.pop(key, None)
    if event:
        event.set()  # release all waiting requests


def store_request_body(key, body):
    request_bodies[key] = body


def get_request_body(key):
    return request_bodies.get(key)