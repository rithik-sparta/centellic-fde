bold=$(tput bold)
normal=$(tput sgr0)


echo "TEST ${bold}Test ${normal}"
curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"title": "Canada Market Outlook", "firm_id": 310}' | jq

curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"title": "Canada Market Outlook", "firm_id": 310}' | jq

curl -X GET http://127.0.0.1:8000/reports | jq