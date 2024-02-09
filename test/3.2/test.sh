VALIDATE=../node_modules/hapi-server-verifier/validate.js
node $VALIDATE TestData3.2-catalog-all.json | tee TestData3.2-catalog-all.json.log
node $VALIDATE TestData3.2-catalog-all-stringType.json | tee TestData3.2-catalog-all-stringType.json.log
node $VALIDATE TestData3.2-about.json | tee TestData3.2-about.json.log
