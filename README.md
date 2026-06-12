# Idempotency Gateway (Pay-Once Protocol)

A RESTful payment processing API that prevents duplicate transactions using an idempotency key.

This project simulates a payment gateway where a request is processed exactly once, even if the client retries the request due to network failures.

---

# Project Overview

Payment systems can receive duplicate requests when clients retry after timeouts.

The Idempotency Gateway solves this problem by:

* Accepting a unique `Idempotency-Key`
* Processing new payment requests once
* Saving the original response
* Returning the saved response for duplicate requests
* Rejecting reused keys with different payment data

---

# Features

* Idempotent payment processing
* Duplicate payment prevention
* Request payload validation
* Conflict detection
* Concurrent request protection
* Cached response replay
* Swagger UI API testing
* In-memory transaction storage

---

# Architecture Diagram

## Request Flow

```mermaid
flowchart TD

A[Client / E-commerce System] --> B[Idempotency Gateway API]

B --> C{Check Idempotency-Key}

C -->|Existing Key| D[Return Saved Response]

D --> E[Response + X-Cache-Hit:true]

C -->|New Key| F[Lock Processing State]

F --> G[Process Payment]

G --> H[Generate Response]

H --> I[Store Payment Result]

I --> J[Return Success Response]

C -->|Same Key Different Payload| K[409 Conflict]
```

---

## Sequence Diagram

```mermaid
sequenceDiagram

Client->>API: POST /process-payment

API->>Store: Check Idempotency-Key

alt Key already exists

Store-->>API: Saved response

API-->>Client: Return cached response

else New request

API->>Store: Mark processing

API->>Payment Service: Process payment

Payment Service-->>API: Payment result

API->>Store: Save response

Store-->>API: Stored transaction

API-->>Client: Success response

end
```

---

# Technology Stack

* Python
* Flask
* Flasgger (Swagger UI)
* In-memory storage

---

# Project Structure

```
Idempotency-Gateway/

│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── store.py
│   ├── models.py
│   ├── service.py
│   └── utils.py
│
├── tests/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/oelshadai/Idempotency-Gateway.git
```

Move into the project folder:

```bash
cd Idempotency-Gateway
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Application

Start the server:

```bash
python main.py
```

The API runs on:

```
http://127.0.0.1:5000
```

---

# Swagger API Documentation

Open:

```
http://127.0.0.1:5000/apidocs/
```

Swagger UI allows testing the API directly from the browser.

---

# API Documentation

## Process Payment

### Endpoint

```
POST /process-payment
```

---

## Required Headers

```
Content-Type: application/json

Idempotency-Key: unique-payment-key
```

---

## Request Body

Example:

```json
{
  "amount": 100,
  "currency": "GHS"
}
```

---

# First Payment Request

Request:

```
Idempotency-Key: payment123
```

Response:

```json
{
    "status": "success",
    "message": "Charged 100 GHS"
}
```

The payment is processed and the response is stored.

---

# Duplicate Request

Sending the same request again:

```
Idempotency-Key: payment123
```

Response:

```json
{
    "status": "success",
    "message": "Charged 100 GHS"
}
```

Header:

```
X-Cache-Hit: true
```

The payment is not processed again.

---

# Conflict Handling

If the same key is reused with different data:

Request:

```json
{
    "amount": 500,
    "currency": "GHS"
}
```

Using:

```
Idempotency-Key: payment123
```

Response:

```json
{
    "error":
    "Idempotency key already used for a different request body."
}
```

Status:

```
409 Conflict
```

---

# Design Decisions

## In-Memory Storage

A dictionary-based store was used to simulate a fast key-value database.

The store keeps:

* Idempotency key
* Request hash
* Payment response
* Processing state

---

## Request Hashing

Each payment request body is hashed.

This prevents:

* Using the same key for another payment
* Accidental duplicate transactions
* Data inconsistency

---

## Concurrency Handling

The system tracks requests currently being processed.

When two identical requests arrive at the same time:

1. First request starts processing
2. Second request detects the processing state
3. Second request waits
4. First request completes
5. Stored response is returned

This prevents race conditions and double charging.

---

# Developer's Choice Feature

## In-Flight Request Protection

A real payment system can receive multiple retries while the first payment is still processing.

The implemented protection ensures:

* Only one payment process starts
* Other identical requests wait
* The final result is reused

This improves reliability and customer protection.

---

# Testing

The API can be tested using:

* Swagger UI
* Postman
* curl

Test scenarios:

1. First payment request
2. Duplicate request with same key
3. Same key with different payload
4. Concurrent requests

---

# Author

Osei Elshadai
