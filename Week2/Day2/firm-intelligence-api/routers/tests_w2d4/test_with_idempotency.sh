bold=$(tput bold)
normal=$(tput sgr0)


echo "TEST ${bold}Test ${normal}"

# First request - creates report with ID 3
curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: abc-123" \
  -d '{"title": "Canada Market Outlook", "firm_id": 310}' | jq

# Second request with same key - returns same report (ID 3, not 4)
curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: abc-123" \
  -d '{"title": "Canada Market Outlook", "firm_id": 310}' | jq

# Same key with different data - error
curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: abc-123" \
  -d '{"title": "Different Report", "firm_id": 999}' | jq