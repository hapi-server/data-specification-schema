fs = require("fs")
about = {
  "id": "TestData3.3",
  "title": "Server using HAPI 3.3 additions",
  "HAPI": "3.3",
  "contact": "rweigel@gmu.edu",
  "serverCitation": "DOI",
  "note": ["note 1", "note 2"],
  "warning": ["warning 1", "warning 2"],
  "status": {
    "message": "OK"
  }
}
fs.readFile("HAPI-3.3.json", (err, buff) => {
  if (!err) {
    schema = buff.toString()
    schema = JSON.parse(schema)
    const Ajv = require("ajv");
      const ajv = new Ajv();
      const validate = ajv.compile(schema);
      v = validate(about)
      if (!v) {
        console.log("Validation errors:")
        console.log(JSON.stringify(validate.errors, null, 2))
      }
      console.log(v)
    return
  }
})

