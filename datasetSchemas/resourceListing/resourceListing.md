Additional constraints can apply to the `parameters` array (such as required parameters, parameter names, types, order, and meaning) and other parts of the full `/info` response. (Note that a subset of parameters requested from an `/info` response may omit parameters required by the schema; `datasetSchema` applies to the full `/info` response.)

#### 3.6.15.1 `resourceListing` Schema

A dataset with `"datasetSchema": "resourceListing"` is a time-ordered listing of resources, such as data files or images. HAPI already permits URI-valued string parameters through `stringType`; the `resourceListing` schema additionally standardizes parameter names and meanings so clients can recognize and process such listings consistently.

This schema does not change the [existing recommendation](#366-stringtype-object) to provide underlying numeric time-series data directly through HAPI when practical, rather than only offering resource URIs.

The full `parameters` array must begin with `startDate` (type `isotime`) followed by `uri` (type `string` with `stringType` of `uri`). Each record's `startDate` represents the beginning of the resource's **data coverage interval**, not the time the resource was created or modified. Accordingly, the dataset-level `timeStampLocation` **must** be `begin` (rather than the usual HAPI default of `center`).

The other parameters in the table below are optional and may appear in any order after the two required parameters. Additional, non-standard parameters are allowed, but their names **must** begin with `x_` and must not conflict with the standard names in this table.

**`resourceListing` `/info` requirements **

| Dataset Attribute | Type | Requirement | Description |
|----------------|------|-------------|-------------|
| `timeStampLocation` | `string` | **Required** | Must have value of `begin` |

**`resourceListing` parameter requirements**

| Parameter name | Type | Requirement | Description |
|----------------|------|-------------|-------------|
| `startDate` | `isotime` | **Required** | Beginning of the data coverage interval of the resource. |
| `uri` | `string` with `stringType` of `uri` | **Required** | URI identifying the resource (for example, a data file, image, or data endpoint). |
| `modificationDate` | `isotime` | **Recommended** | Time the resource was last modified. |
| `contentLength` | `double` | **Recommended** | Size of the resource in bytes (required: `units`: `B`), when applicable and known. See the additional discussion below regarding formatting. |
| `checksum` | `string` with `stringType` of `checksum` | Optional | Checksum digest for the resource; the algorithm is specified in `stringType`. |
| `creationDate` | `isotime` | Optional | Time the resource was created. |
| `accessDate` | `isotime` | Optional | Time the resource was last accessed. |
| `stopDate` | `isotime` | Optional | Exclusive end of the data coverage interval of the resource. |
| `version` | `string` | Optional | Project-specific resource version identifier; no particular format is required. |

The following rules and conventions apply:

- URI values should identify retrievable, data-oriented resources rather than unrelated actions (such as `mailto:` links). The existing `stringType` URI rules apply, including the optional `base`, `scheme`, and `mediaType` attributes; `mediaType` should be supplied when known.
- `size` must be non-negative and integer-valued, even though its HAPI type is `double`. HAPI's `integer` type is limited to signed 32-bit values. All integer byte counts through 9,007,199,254,740,991 (2^53 - 1) can be represented exactly by a double-precision value; larger counts may lose precision. Scientific notation can be used for large values but does not restore exactness.
- If `checksum` is present, its `stringType` must identify the checksum algorithm as described in the [`stringType` section](#366-stringtype-object). The data values contain checksum digests, not algorithm names.
- As for all HAPI datasets, the primary time values must be non-decreasing; duplicate `startDate` values are allowed.

The top-level `/info` attributes `startDate` and `stopDate` describe the time range of the *listing dataset*. They are distinct from the per-resource `startDate` and optional `stopDate` parameters described above.

**Accuracy of resource coverage times**

Ideally, a server should report the actual beginning and exclusive end of the data coverage of each resource. However, determining exact times may require reading individual files. When this is impractical, a server may report conservative nominal coverage times, provided the reported interval encompasses all data in the resource. In particular, `startDate` must not be later than the earliest covered data, and, when `stopDate` is provided, it must be later than the latest covered data. These bounds can be calculated in advance or obtained from existing metadata; the server need not inspect every resource for each request.

For example, a file containing burst observations during one hour may be listed with a nominal interval covering the entire UTC day. An interval covering the actual burst hour is preferable, and exact times are best. Conservative intervals may cause clients to retrieve more candidate resources than necessary, but should not exclude resources that actually contain relevant data. Servers should include the optional `stopDate` whenever its value is known, particularly when clients may need to search for overlapping resources.

**Time-range requests and overlapping resources**

A `/data` request for a `resourceListing` dataset follows the same time-range rules as any other HAPI dataset: the server **must** return only records whose `startDate` is within the requested range (`start` inclusive, `stop` exclusive). The request does **not** select records based on whether the resource's coverage interval overlaps the requested range. A server must not return a record with an earlier `startDate` merely because its resource contains data in the requested interval.

For example, suppose a data line in a `resourceListing` has `startDate = 2026-03-02T00:00:00Z` and `stopDate = 2026-03-03T00:00:00Z`. A HAPI `/data` request for `start=2026-03-02T12:00:00Z&stop=2026-03-02T13:00:00Z` will **not** return that record, even if the resource contains observations during that hour. This is standard HAPI behavior but may be unexpected for a resource listing.

Clients that need **all resources containing data in a time range** should therefore request a sufficiently broad interval to include resources whose `startDate` precedes the desired interval, then use the per-resource coverage times to identify possible overlaps. When `stopDate` is provided, a reported resource interval overlaps a requested interval if `resource.startDate < request.stop` and `resource.stopDate > request.start`. If `stopDate` is absent, clients may need to inspect the resource or use other metadata to determine its end time. Nominal intervals can yield extra possible matches; clients may need to trim the data after retrieval.

The extent to which clients must broaden the request depends on the maximum possible resource duration or other knowledge of how resources are organized. If no such bound is known, a client cannot guarantee finding every overlapping resource with an arbitrarily short `/data` request. In that case, it may need to query from the beginning of the listing's available time range (possibly in batches, subject to server request limits).

Clients should not assume that every returned resource overlaps their target interval or that a narrow query returns every overlapping resource. They should also be prepared for imperfect metadata. For example, if a server omits the required `timeStampLocation: "begin"`, clients interpreting a `resourceListing` should still treat its `startDate` parameter as the beginning of the reported resource coverage interval, and may warn that the server is not conformant.

**Example `/info` response**

```json
{
  "HAPI": "3.4",
  "status": {"code": 1200, "message": "OK"},
  "startDate": "2022-11-01T00:00:00Z",
  "stopDate": "2026-03-06T00:00:00Z",
  "datasetSchema": "resourceListing",
  "timeStampLocation": "begin",
  "parameters": [
    {
      "name": "startDate",
      "type": "isotime",
      "length": 20,
      "units": "UTC",
      "fill": null
    },
    {
      "name": "uri",
      "type": "string",
      "stringType": {
        "uri": {
          "base": "https://example.org/data/images/",
          "mediaType": "image/jpeg"
        }
      },
      "length": 128,
      "units": null,
      "fill": null
    },
    {
      "name": "modificationDate",
      "type": "isotime",
      "length": 20,
      "units": "UTC",
      "fill": null
    },
    {
      "name": "size",
      "type": "double",
      "units": "B",
      "fill": null
    },
    {
      "name": "checksum",
      "type": "string",
      "stringType": {"checksum": {"algorithm": "sha-256"}},
      "length": 64,
      "units": null,
      "fill": null
    }
  ]
}
```

# Resource Listing Schema

| parameter name | parameter type | required / recommended / optional |  description |
|-----------|---------|-----|------------|
| `startDate` | `isotime` | required | start date/time of coverage |
| `uri`    | `string` (and `stringType` of `uri`) | required | name of resource (file, image, endpoint, etc) |
 `modificationDate` | `isotime` | recommended | last modified time of the resource |
| `size` | number - see below | recommended | size of the file in `B` (bytes) |
| `checksum` | `string` (and `stringType` constrains the `checkSumAlgorithm`) | optional | value for checksum with the specified algorithm |
| `creationDate` | `isotime` | optional | time the resource was created |
| `accessDate` | `isotime` | optional | date & time the resource was last accessed |
| `stopDate` | `isotime` | optional | stop date & time of coverage; exclusive (like HAPI request end times) |
| `version`  | `string` | optional |  project-specific version indicator |

# About `startDate` and `stopDate`

How accurate should the `startDate` and `stopDate` be?  Are the day boundary times good enough, or should the server open up the file to get actual times (and thus have to save those out somewhere!!)?

Recommendations:

* Use case:  "I want all the files that contain data in this time range."
* Response of server: It is OK to report more files (that have data outside the requested range, so that the data in the listed files needs to be trimmed if needed), but it is not OK to report fewer files so that some of the data in the requested time range comes from files that did not get returned in the list.
* The best solution is to have the file listing report exact start and stop times for the content of each file.
* Ok solutions are to report nominal times for files, as long as the main use case is met (all files with data in given time range are returned).

# About the `contentLength` 

Units must be in `B` and type `double`. Servers should format values in CSV as integers, unless the `contentLength` is greater than `9,007,199,254,740,991` (~9 PB), in which case scientific notation should be used. Note that with this approach, a `contentLength` greater than ~9 PB cannot be represented with an exact number of bytes.

# About Version Numbers

There are no constraints on the version strings. If there are multiple version of files over the life of a project, it may be desirable to offer a version indicator to distinguish between subsequent revisions (better calibration, revised background subtraction, etc).
