VADLIDATE=../node_modules/hapi-server-verifier/validate.js
node $VADLIDATE refs.json | tee refs.json.log
node $VADLIDATE TestData3.1-dataset1.json | tee TestData3.1-dataset1.json.log
node $VADLIDATE TestData3.1-dataset1-Aα☃.json | tee TestData3.1-dataset1-Aα☃.json.log
node $VADLIDATE TestData3.1-dataset2.json | tee TestData3.1-dataset2.json.log