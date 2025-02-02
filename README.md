JSON Schema for HAPI JSON Responses

# Testing

```
git clone https://github.com/hapi-server/verify-nodejs
git clone https://github.com/hapi-server/data-specification-schema
cd verify-nodejs
npm install
rm -f data-specification-schema
ln -s ../data-specification-schema
cd ../data-specification-schema/test
npm install glob
node test.js # or, e.g., node test.js 3.3
```

The schema files in this repository (`HAPI-data-access-schema-*`) are used for testing.

# Formatting

Prior to committing, execute

```
node util/reformat.js FILENAME.js
```

# Pull Requests

Please post an issue prior to creating a pull request. Pull request must have an associated unit test.

# Contact

Submit questions, bug reports, and feature requests to the [issue tracker](https://github.com/hapi-server/data-specification-schema/issues).
