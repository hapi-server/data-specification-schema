VADLIDATE=../node_modules/hapi-server-verifier/validate.js
node $VADLIDATE TestData3.2-catalog-all.json | tee TestData3.2-catalog-all.json.log
node $VADLIDATE TestData3.2-catalog-all-stringType.json | tee TestData3.2-catalog-all-stringType.json.log
