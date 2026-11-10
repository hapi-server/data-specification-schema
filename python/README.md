# Overview

This directory contains a Python script for performing JSON schema validation.

# Examples

```bash
python3 -m pip install -r requirements.txt
python3 validate.py --help

python3 validate.py resourceListing/example1.json --endpoint info
python3 validate.py resourceListing/example1.json --endpoint info --local

python3 validate.py 'https://cottagesystems.com/server/cdaweb/hapi/info?id=WI_SOSP_3DP/source' --endpoint info

python3 validate.py --version 3.4 'https://cottagesystems.com/server/cdaweb/hapi/info?id=WI_SOSP_3DP/source' --endpoint info
```

The source may be a local JSON file or an HTTP(S) URL. Quote URLs containing shell-special characters such as `&`. URL responses undergo the same main and dataset schema checks as local files; `--local` only affects dataset schemas.

The schema version comes from the source's `HAPI` field. Optional `--version`
overrides that selection. Validation aborts if the selected version is missing
or invalid, or its schema file cannot be read. Schemas are loaded from
`HAPI-data-access-schema-VERSION.json` one directory above the script.
The override does not modify the source: its `HAPI` field must still pass
the selected schema. `--schema` is no longer supported.

`--endpoint` is required and selects a schema part such as `about`, `catalog`,
or `info`. `/info` and `#/info` are also accepted; `#` selects the schema root.

If the JSON to be validated has a `datasetSchema` or `x_datasetSchema` node, the schema pointed to by `datasetSchema.schemaURI` is downloaded and an additional validation against this schema is performed. The dataset schema is downloaded to `./tmp/datasetSchema.json` on each run. However, if `--local`, no dataset schema download occurs. The local file `schemaName/schemaName.json` is used instead, where `schemaName` is the name in `datasetSchema.schemaName`.
