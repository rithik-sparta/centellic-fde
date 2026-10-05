bold=$(tput bold)
normal=$(tput sgr0)


echo "TEST ${bold}Test put is idempotent${normal}"

curl -X PUT http://127.0.0.1:8000/reports/2 \
  -H "Content-Type: application/json" \
  -d '{"title": "Canada Market Outlook", "firm_id": 42}' | jq

curl -X PUT http://127.0.0.1:8000/reports/2 \
  -H "Content-Type: application/json" \
  -d '{"title": "Canada Market Outlook", "firm_id": 42}' | jq

