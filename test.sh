#!/bin/bash

curl \
  --header "Content-Type: application/json" \
  -d '{"name": "Foobar Binbazen The Elder", "company": "Acme Inc. Super Company", "host": "Santa Clause", "email": "foo@example.com", "days": 3}' \
  http://localhost:5000/
