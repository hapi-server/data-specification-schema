Experiment using AJV instead of jsonschema package.

Error messages are just as opaque. However, only need to pass full schema - no need to set subschemas.

Notes "top level needs has; not other places, but still works". I think this means that ids that were referenced in JSON references need hashes. Seems to be inconsistency with what VS Code validator expects. See diff on HAPI-3.3.json and ../../HAPI-data-access-specification-3.3.json.