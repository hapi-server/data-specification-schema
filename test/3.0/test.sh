VALIDATE=../node_modules/hapi-server-verifier/validate.js
node $VALIDATE error.json | tee error.json.log
node $VALIDATE refs.json | tee refs.json.log
node $VALIDATE TestData3.0-dataset1.json | tee TestData3.0-dataset1.json.log
node $VALIDATE TestData3.0-dataset1-resolved.json | tee TestData3.0-dataset1-resolved.json.log
node $VALIDATE TestData3.0-about.json | tee TestData3.0-about.json.log
