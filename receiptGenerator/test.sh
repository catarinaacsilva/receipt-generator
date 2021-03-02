#!/usr/bin/env bash

URL="http://127.0.0.1:8000/receipt?version=1&policy=abc&consent=accept&controller=controller"
RESPONSE=$(curl -L -sb -H "Accept: application/json" $URL)
echo -e $RESPONSE