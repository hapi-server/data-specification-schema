To use the VSCode JSON validator to check the validity of HAPI JSON files, one can add a `$schema` node in the file that points to a file that in turn points to the actual HAPI schema file and a subschema such as `info`. (If we split the `info` part out of the HAPI schema into a single file, one could directly point to that file using `$schema` to validate an `info` JSON file. However, there are many complications to splitting up the HAPI schema.)

Technically, `$schema` should always point to a version of the JSON schema schema, e.g., http://json-schema.org/draft-07/schema#. However, VSCode will validate against a schema using this technique.

At present, it is not possible to have `$schema` point directly to the HAPI JSON schema and have validators use it because it is non-standard. See [json-schema-org/json-schema-spec#828](https://github.com/json-schema-org/json-schema-spec/issues/828).

See also
* https://github.com/hapi-server/data-specification/issues/134
* https://github.com/hapi-server/data-specification-schema/issues/7
* https://github.com/hapi-server/data-specification-schema/issues/6
* https://github.com/hapi-server/data-specification-schema/issues/3