import time

def process_payment(amount, currency):
    time.sleep(2)  # simulate delay

    return {
        "status": "success",
        "message": f"Charged {amount} {currency}"
    }