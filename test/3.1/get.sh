SERVER="https://hapi-server.org/servers/TestData3.1/hapi/info"
#SERVER="http://localhost:8999/TestData3.1/hapi/info"
curl "$SERVER?id=dataset1" > TestData3.1-dataset1.json
curl -G "$SERVER" --data-urlencode "id=dataset1-Aα☃" > TestData3.1-dataset1-Aα☃.json
curl "$SERVER?id=dataset2" > TestData3.1-dataset2.json
