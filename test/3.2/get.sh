#SERVER="https://hapi-server.org/servers/TestData3.2/hapi"
SERVER="http://localhost:8998/TestData3.2/hapi"
curl "$SERVER/catalog?depth=all" > TestData3.2-catalog-all.json
