#!/usr/bin/env bash

# Generate a new receipt

echo -e "Generate a new receipt "
curl -s -X GET "http://localhost:8000/receiptGenerator?version=1&policy=policy&consent=true&controller=controller" | jq .

#************************************************************************************************************************************

# Add signed receipt

echo -e "Store receipt"
curl -s -d "{\"json_receipt\": \"recibo\", \"email\":\"myemail@email.com\", \"state\":\"true\"}" \
-H "Content-Type: application/json" http://localhost:8000/storeReceipt | jq .


#************************************************************************************************************************************


# Return all the receipts id given the email

echo -e "Return all the receipts id given the email"
curl -s -X GET "http://localhost:8000/getReceipt?email=myemail@email.com" | jq .


#************************************************************************************************************************************

# Remove receipts

echo -e "Remove receipts"
curl -s -d "{\"email\":\"myemail@email.com\"}" \
-H "Content-Type: application/json" http://localhost:8000/removeReceipt | jq .


# Return all the receipts id given the email

echo -e "Return all the receipts id given the email"
curl -s -X GET "http://localhost:8000/getReceipt?email=myemail@email.com" | jq .

#************************************************************************************************************************************

# Add signed receipt

echo -e "Store receipt"
curl -s -d "{\"json_receipt\": \"recibo\", \"email\":\"myemail@email.com\", \"state\":\"true\"}" \
-H "Content-Type: application/json" http://localhost:8000/storeReceipt | jq .

sleep 1.5

echo -e "Store receipt"
curl -s -d "{\"json_receipt\": \"recibo\", \"email\":\"myemail@email.com\", \"state\":\"false\"}" \
-H "Content-Type: application/json" http://localhost:8000/storeReceipt | jq .

# Return all the receipts id given the email

echo -e "Return all the receipts id given the email"
curl -s -X GET "http://localhost:8000/getReceipt?email=myemail@email.com" | jq .

# Return the most recent receipt id for the given email

echo -e "Return the most recent receipt id for the given email"
curl -s -X GET "http://localhost:8000/getRecentReceipt?email=myemail@email.com" | jq .

#************************************************************************************************************************************

# Return the state for all the receipts

#echo -e "Return the state for all the receipts"
#curl -s -X GET "http://localhost:8000/getReceiptAllState?email=myemail@email.com" | jq .

#************************************************************************************************************************************


echo -e "Store receipt"
content=$(curl -s -d "{\"json_receipt\": \"recibostate\", \"email\":\"statemyemail@email.com\", \"state\":\"false\"}" \
-H "Content-Type: application/json" http://localhost:8000/storeReceipt | jq .) 
id_receipt=$( jq -r  '.id_receipt' <<< "${content}" ) 
echo "${id_receipt}"

# Return the state for a given receipt

echo -e "Return the most recent receipt id for the given email"
curl -s -X GET "http://localhost:8000/getReceiptState?email=statemyemail@email.com&id_receipt=$id_receipt" | jq .

