VADLIDATE=../node_modules/hapi-server-verifier/validate.js
node $VADLIDATE error.json | tee error.json.log
node $VADLIDATE refs.json | tee refs.json.log
node $VADLIDATE TestData3.0-dataset1.json | tee TestData3.0-dataset1.json.log
node $VADLIDATE TestData3.0-dataset1-resolved.json | tee TestData3.0-dataset1-resolved.json.log
node $VADLIDATE TestData3.0-about.json | tee TestData3.0-about.json.log
