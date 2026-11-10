from argparse import Namespace
import contextlib
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch


BASE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("hapi_validate", BASE / "validate.py")
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.response = self.root / "response.json"
        self.schema = self.root / "main.json"
        self.schema.write_text(json.dumps({
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": {"string": {"type": "string"}},
            "info": {
                "type": "object",
                "required": ["value"],
                "properties": {"value": {"$ref": "#/definitions/string"}},
            },
        }))
        self.data = {
            "value": "ok",
            "datasetSchema": {
                "schemaName": "resourceListing",
                "schemaURI": "https://example.org/python/resourceListing/schema.json"
            },
        }
        self.response.write_text(json.dumps(self.data))
        self.secondary = {"required": ["value"], "properties": {"value": {"const": "ok"}}}

    def run_cli(self, *extra, schema=None, fragment="/info", source=None):
        args = [
            "validate.py", str(self.response if source is None else source),
            "--schema", str(schema or self.schema),
        ]
        if fragment is not None:
            args += ["--fragment", fragment]
        args += list(extra)
        output, errors = io.StringIO(), io.StringIO()
        with patch("sys.argv", args), patch.object(Path, "cwd", return_value=self.root):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                try:
                    code = validate.main()
                except SystemExit as error:
                    code = error.code
        return code, output.getvalue(), errors.getvalue()

    def local_schema(self, schema=None):
        path = self.root / "resourceListing" / "resourceListing.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(self.secondary if schema is None else schema))
        return path

    def test_fragment_required(self):
        self.assertEqual(self.run_cli(fragment=None)[0], 2)

    def test_cli_arguments(self):
        for local in (False, True):
            with self.subTest(local=local):
                args = [
                    "validate.py", "response.json",
                    "--schema", "3.2", "--fragment", "/info",
                ]
                if local:
                    args.append("--local")
                with patch("sys.argv", args):
                    parsed = validate.cli()
                self.assertEqual(parsed.response, "response.json")
                self.assertEqual(parsed.schema, "3.2")
                self.assertEqual(parsed.fragment, "/info")
                self.assertEqual(parsed.local, local)

    def test_internal_references_and_local_secondary(self):
        self.local_schema()
        with patch.object(validate, "urlopen") as download:
            code, output, errors = self.run_cli("--local", fragment="#/info")
        self.assertEqual(code, 0, errors)
        self.assertIn(f"Valid: {self.root / 'resourceListing/resourceListing.json'}#", output)
        download.assert_not_called()

    def test_validate_hapi_call(self):
        args = Namespace(schema=str(self.schema), fragment="/info", local=False)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertTrue(validate.validate(
                self.data, "HAPI", args
            ))
            args.fragment = "#/info"
            self.assertFalse(validate.validate(
                {"value": 1}, "HAPI", args
            ))

    def test_validate_dataset_schema_call(self):
        self.local_schema()
        args = Namespace(schema=str(self.schema), fragment="/info", local=True)
        with patch.object(Path, "cwd", return_value=self.root):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertTrue(validate.validate(
                    self.data, "datasetSchema", args
                ))
                self.data["value"] = "wrong"
                self.assertFalse(validate.validate(
                    self.data, "datasetSchema", args
                ))

    def test_validate_unknown_stage(self):
        with self.assertRaisesRegex(ValueError, "Unknown validation stage"):
            validate.validate(self.data, "unknown", Namespace())

    def test_version_schema_and_main_failure(self):
        sample = json.loads((BASE / "resourceListing/example1.json").read_text())
        self.response.write_text(json.dumps(sample))
        with patch.object(validate, "urlopen") as download:
            download.return_value.__enter__.return_value.read.return_value = b"true"
            code, _, errors = self.run_cli(schema="3.4")
        self.assertEqual(code, 1, errors)
        self.assertIn("datasetSchema", errors)
        download.assert_called_once_with(sample["datasetSchema"]["schemaURI"], timeout=30)

    def test_version_schema_passes_without_dataset_schema(self):
        sample = json.loads((BASE / "resourceListing/example1.json").read_text())
        del sample["datasetSchema"]
        self.response.write_text(json.dumps(sample))
        self.assertEqual(self.run_cli(schema="3.4")[0], 0)

    def test_versioned_schemas_resolve_references_and_enforce_constraints(self):
        for version in ("3.0", "3.1", "3.2", "3.3", "3.4"):
            with self.subTest(version=version):
                response = {
                    "HAPI": version,
                    "status": {"code": 1200, "message": "OK"},
                    "startDate": "2026-01-01T00:00:00Z",
                    "stopDate": "2026-02-01T00:00:00Z",
                    "parameters": [
                        {"name": "Time", "type": "isotime", "length": 20,
                         "units": "UTC", "fill": None},
                        {"name": "value", "type": "double",
                         "units": "nT", "fill": None},
                    ],
                }
                self.response.write_text(json.dumps(response))
                code, _, errors = self.run_cli(schema=version)
                self.assertEqual(code, 0, errors)
                response["parameters"][1]["type"] = "invalid"
                self.response.write_text(json.dumps(response))
                code, _, errors = self.run_cli(schema=version)
                self.assertEqual(code, 1, errors)
                self.assertIn("HAPI $.parameters[1].type", errors)

    def test_legacy_references_in_secondary_schema(self):
        self.local_schema({
            "check": {"id": "/check", **self.secondary},
            "$ref": "/check",
        })
        code, _, errors = self.run_cli("--local")
        self.assertEqual(code, 0, errors)
        self.data["value"] = "wrong"
        self.response.write_text(json.dumps(self.data))
        code, _, errors = self.run_cli("--local")
        self.assertEqual(code, 1, errors)
        self.assertIn("datasetSchema $.value", errors)

    def test_download_and_secondary_validation(self):
        content = json.dumps(self.secondary).encode()
        with patch.object(validate, "urlopen") as download:
            download.return_value.__enter__.return_value.read.return_value = content
            code, output, errors = self.run_cli()
        self.assertEqual(code, 0, errors)
        self.assertEqual((self.root / "tmp/schema.json").read_bytes(), content)
        self.assertIn(f"Valid: {self.root / 'tmp/schema.json'}#", output)
        download.assert_called_once_with(
            self.data["datasetSchema"]["schemaURI"], timeout=30
        )

    def test_secondary_failure(self):
        self.local_schema({"properties": {"value": {"const": "different"}}})
        code, _, errors = self.run_cli("--local")
        self.assertEqual(code, 1)
        self.assertIn("datasetSchema $.value", errors)

    def test_local_uses_schema_name_not_uri(self):
        self.local_schema()
        self.data["datasetSchema"]["schemaURI"] = "https://example.org/other.json"
        self.response.write_text(json.dumps(self.data))
        self.assertEqual(self.run_cli("--local")[0], 0)

    def test_local_does_not_require_uri(self):
        self.local_schema()
        del self.data["datasetSchema"]["schemaURI"]
        self.response.write_text(json.dumps(self.data))
        with patch.object(validate, "urlopen") as download:
            self.assertEqual(self.run_cli("--local")[0], 0)
        download.assert_not_called()

    def test_x_dataset_schema_local(self):
        self.local_schema()
        self.data["x_datasetSchema"] = self.data.pop("datasetSchema")
        self.response.write_text(json.dumps(self.data))
        code, output, errors = self.run_cli("--local")
        self.assertEqual(code, 0, errors)
        self.assertIn(f"Valid: {self.root / 'resourceListing/resourceListing.json'}#", output)

    def test_dataset_schema_arrays(self):
        self.local_schema()
        other = self.root / "other" / "other.json"
        other.parent.mkdir()
        other.write_text('{"required": ["missing"]}')
        for key in ("datasetSchema", "x_datasetSchema"):
            with self.subTest(key=key):
                node = {"schemaName": "resourceListing"}
                self.response.write_text(json.dumps({"value": "ok", key: [node]}))
                code, output, errors = self.run_cli("--local")
                self.assertEqual(code, 0, errors)
                self.assertIn(f"Valid: {self.root / 'resourceListing/resourceListing.json'}#", output)
                self.response.write_text(json.dumps({
                    "value": "ok", key: [node, {"schemaName": "other"}]
                }))
                code, _, errors = self.run_cli("--local")
                self.assertEqual(code, 1, errors)
                self.assertIn(f"{key}[1] $", errors)
                for invalid in ([], [None]):
                    self.response.write_text(json.dumps({"value": "ok", key: invalid}))
                    self.assertEqual(self.run_cli("--local")[0], 2)

    def test_x_dataset_schema_download(self):
        self.data["x_datasetSchema"] = self.data.pop("datasetSchema")
        self.data["x_datasetSchema"]["schemaURI"] = "https://example.org/schema.json"
        self.response.write_text(json.dumps(self.data))
        with patch.object(validate, "urlopen") as download:
            download.return_value.__enter__.return_value.read.return_value = (
                json.dumps(self.secondary).encode()
            )
            code, output, errors = self.run_cli()
        self.assertEqual(code, 0, errors)
        self.assertIn(f"Valid: {self.root / 'tmp/schema.json'}#", output)
        self.assertTrue((self.root / "tmp/schema.json").is_file())

    def test_both_dataset_schema_nodes_are_validated(self):
        self.local_schema()
        self.data["x_datasetSchema"] = {"schemaName": "other"}
        self.response.write_text(json.dumps(self.data))
        path = self.root / "other" / "other.json"
        path.parent.mkdir()
        path.write_text('{"required": ["missing"]}')
        code, output, errors = self.run_cli("--local")
        self.assertEqual(code, 1)
        self.assertIn(f"Valid: {self.root / 'resourceListing/resourceListing.json'}#", output)
        self.assertIn("x_datasetSchema $", errors)

    def test_http_download(self):
        content = json.dumps(self.secondary).encode()
        data = self.data
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(data).encode() if self.path.startswith("/info?") else content
                )

            def log_message(self, *args):
                pass

        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            worker = threading.Thread(target=server.serve_forever)
            worker.start()
            try:
                self.data["datasetSchema"]["schemaURI"] = (
                    f"http://127.0.0.1:{server.server_port}/resourceListing/schema.json"
                )
                source = f"http://127.0.0.1:{server.server_port}/info?id=example&resolve=true"
                code, _, errors = self.run_cli(source=source)
                self.assertEqual(code, 0, errors)
                self.assertEqual((self.root / "tmp/schema.json").read_bytes(), content)
                self.assertEqual(requests, [
                    "/info?id=example&resolve=true", "/resourceListing/schema.json"
                ])
            finally:
                server.shutdown()
                worker.join()

    def test_url_source_with_local_secondary(self):
        self.local_schema()
        for scheme in ("http", "https"):
            with self.subTest(scheme=scheme):
                source = f"{scheme}://example.org/info?id=example&resolve=true"
                with patch.object(validate, "urlopen") as download:
                    download.return_value.__enter__.return_value.read.return_value = (
                        json.dumps(self.data).encode()
                    )
                    code, output, errors = self.run_cli("--local", source=source)
                self.assertEqual(code, 0, errors)
                self.assertIn(f"Valid: {self.root / 'resourceListing/resourceListing.json'}#", output)
                download.assert_called_once_with(source, timeout=10)

    def test_url_source_main_validation_failure(self):
        with patch.object(validate, "urlopen") as download:
            download.return_value.__enter__.return_value.read.return_value = b'{"value": 1}'
            code, _, errors = self.run_cli(source="https://example.org/info")
        self.assertEqual(code, 1)
        self.assertIn("HAPI $.value", errors)
        self.assertEqual(download.call_count, 1)

    def test_url_source_download_error(self):
        with patch.object(validate, "urlopen", side_effect=OSError("download failed")):
            code, _, errors = self.run_cli(source="https://example.org/info")
        self.assertEqual(code, 2)
        self.assertIn("download failed", errors)

    def test_url_source_invalid_json(self):
        with patch.object(validate, "urlopen") as download:
            download.return_value.__enter__.return_value.read.return_value = b"not JSON"
            code, _, errors = self.run_cli(source="https://example.org/info")
        self.assertEqual(code, 2)
        self.assertIn("Unable to read source", errors)

    def test_url_source_missing_host(self):
        with patch.object(validate, "urlopen") as download:
            code, _, errors = self.run_cli(source="https:///info")
        self.assertEqual(code, 2)
        self.assertIn("host", errors)
        download.assert_not_called()

    def test_secondary_fragment(self):
        self.local_schema({"definitions": {"check": self.secondary}})
        self.data["datasetSchema"]["schemaURI"] += "#/definitions/check"
        self.response.write_text(json.dumps(self.data))
        self.assertEqual(self.run_cli("--local")[0], 0)

    def test_missing_local_schema(self):
        self.assertEqual(self.run_cli("--local")[0], 2)

    def test_download_failure(self):
        with patch.object(validate, "urlopen", side_effect=OSError("download failed")):
            code, _, errors = self.run_cli()
        self.assertEqual(code, 2)
        self.assertIn("download failed", errors)

    def test_no_dataset_schema(self):
        del self.data["datasetSchema"]
        self.response.write_text(json.dumps(self.data))
        with patch.object(validate, "urlopen") as download:
            self.assertEqual(self.run_cli()[0], 0)
        download.assert_not_called()

    def test_invalid_fragment(self):
        self.assertEqual(self.run_cli(fragment="/missing")[0], 2)

    def test_root_fragment(self):
        del self.data["datasetSchema"]
        self.response.write_text(json.dumps(self.data))
        self.schema.write_text('{"required": ["missing"]}')
        self.assertEqual(self.run_cli(fragment="#")[0], 1)

    def test_invalid_dataset_schema(self):
        for node in [None, {}, {"schemaName": "../other"},
                     {"schemaName": "/tmp"}, {"schemaName": ".."},
                     {"schemaName": 1}, {"schemaName": "a\\b"}]:
            with self.subTest(node=node):
                data = copy.deepcopy(self.data)
                data["datasetSchema"] = node
                self.response.write_text(json.dumps(data))
                self.assertEqual(self.run_cli("--local")[0], 2)

    def test_invalid_remote_uri(self):
        for uri in [None, "", "file:///tmp/schema.json", "https://example.org/"]:
            with self.subTest(uri=uri):
                self.data["datasetSchema"]["schemaURI"] = uri
                self.response.write_text(json.dumps(self.data))
                self.assertEqual(self.run_cli()[0], 2)

    def test_json_and_schema_errors(self):
        self.response.write_text("{")
        self.assertEqual(self.run_cli()[0], 2)
        self.response.write_text("{}")
        self.schema.write_text('{"type": "invalid"}')
        self.assertEqual(self.run_cli()[0], 2)


if __name__ == "__main__":
    unittest.main()
