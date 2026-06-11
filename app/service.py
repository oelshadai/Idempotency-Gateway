import time


def process_payment(amount, currency):
    time.sleep(2)

    return {
        "status": "success",
        "message": f"Charged {amount} {currency}"
    }