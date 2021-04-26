#!/usr/bin/env bash

# Generate a new receipt

echo -e "Generate a new receipt "
curl -s -X GET "http://localhost:8000/receiptGenerator?version=1&policy=policy&consent=true&controller=controller" | jq .


# Add signed receipt

echo -e "Store receipt"
curl -s -d "{\"json_receipt\": \"recibo\", \"email\":\"myemail@email.com\", \"state\":\"true\"}" \
-H "Content-Type: application/json" http://localhost:8000/storeReceipt | jq .


# Return all the receipts id given the email

echo -e "Return all the receipts id given the email"
curl -s -X GET "http://localhost:8000/getReceipt?email=myemail@email.com" | jq .