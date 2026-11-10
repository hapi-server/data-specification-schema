"""Validate a HAPI response and its optional datasetSchema or x_datasetSchema."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urldefrag, urljoin, urlsplit
from urllib.request import urlopen

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT7


def validate(response, stage, args):
    if stage == "HAPI":
        # One directory above this script.
        base = Path(__file__).resolve().parent

        schema_path = (
            base.parent / f"HAPI-data-access-schema-{args.schema}.json"
            if re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", args.schema)
            else Path(args.schema)
        )
        print(f"\nValidating {stage}")
        return validate_schema(response, schema_path, args.fragment, stage)
    if stage != "datasetSchema":
        raise ValueError(f"Unknown validation stage: {stage}")

    if isinstance(response, dict):
        for key in ("datasetSchema", "x_datasetSchema"):
            if key not in response:
                continue
            print(f"\nValidating {stage}")
            nodes = response[key]
            is_array = isinstance(nodes, list)
            if not is_array:
                nodes = [nodes]
            if not nodes:
                raise ValueError(f"{key} must not be an empty array")
            for index, node in enumerate(nodes):
                path, secondary_fragment = dataset_schema_path(node, args.local)
                schema_stage = f"{key}[{index}]" if is_array else key
                if not validate_schema(response, path, secondary_fragment, schema_stage):
                    return False
    return True


def validate_schema(response, schema_path, fragment, stage):

    schema_path = Path(schema_path)
    if not fragment.startswith("#"):
        fragment = "#" + fragment
    with schema_path.open(encoding="utf-8") as stream:
        print(f"  Reading {schema_path}")
        schema = json.load(stream)

    Draft7Validator.check_schema(schema)

    uri = schema_path.resolve().as_uri()
    resource = Resource.from_contents(schema, default_specification=DRAFT7)
    registry = Registry().with_resource(uri, resource)

    # Older HAPI schemas use legacy id-based references under draft-07.
    if isinstance(schema, dict):
        for node in schema.values():
            if isinstance(node, dict):
                legacy_id = node.get("id")
                if isinstance(legacy_id, str) and legacy_id.startswith("/"):
                    registry = registry.with_resource(
                        urljoin(uri, legacy_id),
                        Resource.from_contents(node, default_specification=DRAFT7),
                    )

    validator = Draft7Validator({"$ref": uri + fragment}, registry=registry)

    errors = list(validator.iter_errors(response))

    for error in errors:
        print(f"  Error: {error.json_path}: {error.message}", file=sys.stderr)

    if errors:
        return False

    print("  Valid")

    return True


def dataset_schema_path(node, local):
    if not isinstance(node, dict):
        raise ValueError("dataset schema must be an object")

    if local:
        name = node.get("schemaName")
        if (
            not isinstance(name, str)
            or name in ("", ".", "..")
            or any(character in name for character in ("/", "\\", "\0"))
        ):
            raise ValueError("dataset schemaName must be a nonempty directory name")
        uri = node.get("schemaURI", "")
        if not isinstance(uri, str):
            raise ValueError("dataset schemaURI must be a string when provided")
        _, fragment = urldefrag(uri)
        path = Path.cwd() / name / f"{name}.json"
        return path, "#" + fragment if fragment else "#"

    uri = node.get("schemaURI")
    if not isinstance(uri, str) or not uri:
        raise ValueError("dataset schemaURI must be a nonempty string")
    download_uri, fragment = urldefrag(uri)

    parsed = urlsplit(download_uri)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("dataset schemaURI must be an HTTP(S) URI")

    filename = unquote(parsed.path).split("/")[-1]
    if "\\" in filename or "\0" in filename or not filename.endswith(".json"):
        raise ValueError("schemaURI must end in a .json filename")

    path = Path.cwd() / "tmp" / filename
    with urlopen(download_uri, timeout=30) as response:
        content = response.read()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)

    print(f"  Downloaded {download_uri} to {path}")

    return path, "#" + fragment if fragment else "#"


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response", help="response JSON file or HTTP(S) URL")
    parser.add_argument(
        "--schema",
        required=True,
        help="HAPI version (e.g. 3.4) or path to a HAPI schema",
    )
    parser.add_argument(
        "--fragment",
        required=True,
        help="schema fragment, e.g. /info or #/info; use # for the root",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="read each dataset schema from schemaName/schemaName.json "
        "relative to the working directory instead of downloading, where schemaName is given in the datasetSchema node",
    )
    return parser.parse_args()


def _read_source(args):
    source = urlsplit(args.response)
    if source.scheme in ("http", "https"):
        if not source.netloc:
            raise ValueError("response URL must include a host")
        with urlopen(args.response, timeout=10) as stream:
            response = json.load(stream)
    else:
        with Path(args.response).open(encoding="utf-8") as stream:
            response = json.load(stream)
    return response


def main():
    args = cli()

    try:
        source = _read_source(args)
    except (OSError, ValueError) as error:
        print(f"Unable to read source: {error}", file=sys.stderr)
        return 2

    try:
        # Validate against HAPI schema
        hapi_valid = validate(source, "HAPI", args)

        # Validate against datasetSchema(s), if present
        dataset_valid = validate(source, "datasetSchema", args)
    except (OSError, ValueError, SchemaError, Unresolvable) as error:
        print(f"Unable to validate: {error}", file=sys.stderr)
        return 2

    return 0 if hapi_valid and dataset_valid else 1


if __name__ == "__main__":
    sys.exit(main())
