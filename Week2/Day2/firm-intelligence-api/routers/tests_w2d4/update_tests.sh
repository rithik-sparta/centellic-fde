# curl -i -X POST http://127.0.0.1:8000/firms \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "jurisdiction": "EU", "revenue_usd_m": -755.5, "lawyers": 200, "equity_partners": 300}'


# curl -i -X POST http://127.0.0.1:8000/firms \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "jurisdiction": "EU/USA", "revenue_usd_m": 755.5, "lawyers": 200, "equity_partners": 300}'


# curl -i -X POST http://127.0.0.1:8000/firms \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "jurisdiction": "EU", "revenue_usd_m": 755.5, "lawyers": 880, "equity_partners": 0}'


# curl -i -X POST http://127.0.0.1:8000/firms \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "jurisdiction": "EU", "revenue_usd_m": 755.5, "lawyers": 0, "equity_partners": 300}'


# curl -i -X POST http://127.0.0.1:8000/firms \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "revenue_usd_m": 755.5, "lawyers": 0, "equity_partners": 300}'


# curl -i -X POST http://127.0.0.1:8000/firms \
#   -H "Content-Type: application/json" \
#   -d '{"name": "", "jurisdiction": "EU", "revenue_usd_m": 755.5, "lawyers": 0, "equity_partners": 300}'

bold=$(tput bold)
normal=$(tput sgr0)

# echo "${bold}http://127.0.0.1:8000/firms${normal}"
# curl -X GET http://127.0.0.1:8000/firms | jq

# echo "${bold}http://127.0.0.1:8000/firms?jurisdiction=UK${normal}"
# curl -X GET http://127.0.0.1:8000/firms\?jurisdiction\=UK | jq

# echo "${bold}http://127.0.0.1:8000/firms?jurisdiction=US&revenue_usd_m_gte=2000${normal}"
# curl -X GET http://127.0.0.1:8000/firms\?jurisdiction\=US\&revenue_usd_m_gte\=2000 | jq

# echo "${bold}http://127.0.0.1:8000/firms?revenue_usd_m_gte=1000${normal}"
# curl -X GET http://127.0.0.1:8000/firms?revenue_usd_m_gte\=1000 | jq


echo "${bold}Test update of lawyers and equity_partners${normal}"
curl -X PUT http://127.0.0.1:8000/firms/2 \
  -H "Content-Type: application/json" \
  -d '{"lawyers": 250, "equity_partners": 310}' | jq
echo "${bold}Firm id: 2${normal}"
curl -X GET http://127.0.0.1:8000/firms/2 | jq

echo "${bold}Test no request body, keeps firm data the same${normal}"
curl -X PUT http://127.0.0.1:8000/firms/2 \
  -H "Content-Type: application/json" | jq
echo "${bold}Firm id: 2${normal}"
curl -X GET http://127.0.0.1:8000/firms/2 | jq

echo "${bold}Test invalid revenue_usd_m does not update the model${normal}"
curl -X PUT http://127.0.0.1:8000/firms/2 \
  -H "Content-Type: application/json" \
  -d '{"revenue_usd_m": -755.5, "lawyers": 250, "equity_partners": 310}' | jq
echo "${bold}Firm id: 2${normal}"
curl -X GET http://127.0.0.1:8000/firms/2 | jq

echo "${bold}Test invalid jurisdiction does not update the model${normal}"
curl -X PUT http://127.0.0.1:8000/firms/2 \
  -H "Content-Type: application/json" \
  -d '{"jurisdiction": "UK/EUR"}' | jq
echo "${bold}Firm id: 2${normal}"
curl -X GET http://127.0.0.1:8000/firms/2 | jq

echo "${bold}Test negative lawyers value does not update the model${normal}"
curl -X PUT http://127.0.0.1:8000/firms/2 \
  -H "Content-Type: application/json" \
  -d '{"lawyers": -2}' | jq
echo "${bold}Firm id: 2${normal}"
curl -X GET http://127.0.0.1:8000/firms/2 | jq


# curl -i -X PUT http://127.0.0.1:8000/firms/2 \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "jurisdiction": "EU/USA", "revenue_usd_m": 755.5, "lawyers": 200, "equity_partners": 300}'


# curl -i -X PUT http://127.0.0.1:8000/firms/1 \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "jurisdiction": "EU", "revenue_usd_m": 755.5, "lawyers": 880, "equity_partners": 0}'

# curl -i -X PUT http://127.0.0.1:8000/firms/100 \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ferreira Adeyemi", "jurisdiction": "EU", "revenue_usd_m": 755.5, "lawyers": 880, "equity_partners": 0}'
