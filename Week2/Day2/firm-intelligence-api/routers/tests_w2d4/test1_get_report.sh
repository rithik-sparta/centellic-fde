bold=$(tput bold)
normal=$(tput sgr0)


echo "TEST ${bold}Test get is idempotent${normal}"
curl -X GET http://127.0.0.1:8000/reports/1 | jq
echo "${bold}Make same call again${normal}"
curl -X GET http://127.0.0.1:8000/reports/1 | jq
