SERVER="https://hapi-server.org/servers/TestData3.3/hapi"
#SERVER="http://localhost:8998/TestData3.3/hapi"
curl "$SERVER/about" > TestData3.3-about.json
curl "$SERVER/info?dataset=dataset1" > TestData3.3-dataset1.json
curl "$SERVER/info?dataset=dataset2" > TestData3.3-dataset2.json
