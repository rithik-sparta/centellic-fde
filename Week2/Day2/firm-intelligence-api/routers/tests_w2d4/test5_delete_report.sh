bold=$(tput bold)
normal=$(tput sgr0)


echo "TEST ${bold}Test DELETET${normal}"

curl -X GET http://127.0.0.1:8000/reports/2 | jq
curl -X GET http://127.0.0.1:8000/reports/2 | jq
curl -X GET http://127.0.0.1:8000/reports/2 | jq
curl -X GET http://127.0.0.1:8000/reports/2 | jq
curl -X GET http://127.0.0.1:8000/reports/2 | jq

curl -X GET http://127.0.0.1:8000/reports | jq


curl -X DELETE http://127.0.0.1:8000/reports/2 | jq

curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"title": "Canada Market Outlook", "firm_id": 310}' | jq

curl -X GET http://127.0.0.1:8000/reports/2 | jq