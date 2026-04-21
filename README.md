JSON Schema for HAPI JSON Responses

# Testing

```
git clone https://github.com/hapi-server/verify-nodejs
# Above will result in a dir verify-nodejs/data-specification-schema
# because data-specification-schema repo is git submodule

cd verify-nodejs/data-specification-schema/test
node test.js # or, e.g., node test.js 3.3
```

The schema files in this repository (`HAPI-data-access-schema-*`) are used for testing.

# VS Code

To test JSON files against the HAPI schema in VS Code

# Formatting

Prior to committing, execute

```
node util/reformat.js FILENAME.json
```

so that all JSON files have the same formatting style.

# Pull Requests

Please post an issue prior to creating a pull request. Pull request must have an associated unit test.

# Contact

Submit questions, bug reports, and feature requests to the [issue tracker](https://github.com/hapi-server/data-specification-schema/issues).
