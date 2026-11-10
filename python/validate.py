"""Validate resource listing metadata after the main HAPI schema check."""

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "response",
        nargs="?",
        type=Path,
        default=base / "subschema-sample.json",
        help="response JSON file (default: bundled sample)",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=base / "subschema.json",
        help="second-pass schema (default: bundled subschema.json)",
    )
    args = parser.parse_args()

    try:
        with args.schema.open(encoding="utf-8") as stream:
            schema = json.load(stream)
        with args.response.open(encoding="utf-8") as stream:
            response = json.load(stream)
        Draft7Validator.check_schema(schema)
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError) as error:
        print(f"Unable to validate: {error}", file=sys.stderr)
        return 2

    errors = list(Draft7Validator(schema).iter_errors(response))
    if errors:
        for error in errors:
            print(f"{error.json_path}: {error.message}", file=sys.stderr)
        return 1

    print(f"Valid: {args.response} conforms to {args.schema}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
