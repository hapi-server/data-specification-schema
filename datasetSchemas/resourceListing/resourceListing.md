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

# About the `size` 
Units must be in `B` and values formatted as an integer, unless the `size` is greater than `9,007,199,254,740,991` (~9 PB), in which case scientific notation should be used. Note that with this approach, a `size` is greater than ~9 PB cannot be represented with an exact number of bytes.

# About Version Numbers

There are no constraints on the version strings. If there are multiple version of files over the life of a project, it may be desirable to offer a version indicator to distinguish between subsequent revisions (better calibration, revised background subtraction, etc).
