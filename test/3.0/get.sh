
curl "https://hapi-server.org/servers-dev/TestData3.0/hapi/info?id=dataset1&resolve_references=false" > TestData3.0-dataset1.json
curl "https://hapi-server.org/servers-dev/TestData3.0/hapi/info?id=dataset1" > TestData3.0-dataset1-resolved.json
curl "http://localhost:8998/TestData3.0/hapi/about" > TestData3.0-about.json