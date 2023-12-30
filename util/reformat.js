const fs = require('fs');

let inFile = fs.readFileSync(process.argv[2],'utf8');

let inFileReformatted = JSON.stringify(JSON.parse(inFile),null,2)
fs.writeFileSync(process.argv[2],inFileReformatted,'utf8');
