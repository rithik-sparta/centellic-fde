bold=$(tput bold)
normal=$(tput sgr0)


echo "${bold}Test deleting an existing firm (id 1)${normal}"
echo "${bold}List of all firms${normal}"
curl -X GET http://127.0.0.1:8000/firms | jq
echo "${bold}http://127.0.0.1:8000/firms/1${normal}"
curl -X DELETE http://127.0.0.1:8000/firms/1
echo "${bold}List of all firms${normal}"
curl -X GET http://127.0.0.1:8000/firms | jq


echo "${bold}Test deleting a firm which does not exist${normal}"
echo "${bold}List of all firms${normal}"
curl -X GET http://127.0.0.1:8000/firms | jq
echo "${bold}http://127.0.0.1:8000/firms/100${normal}"
curl -X DELETE http://127.0.0.1:8000/firms/100 | jq
echo "${bold}List of all firms${normal}"
curl -X GET http://127.0.0.1:8000/firms | jq