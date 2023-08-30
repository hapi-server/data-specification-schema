Jon and Jeremy were using https://www.jsonschemavalidator.net to write separate capabilities, about, and 
info response schemas. These can be combined at a future time.  The schema should be loaded in the left
panel, and then the document (about, catalog, info response) is loaded into the right document for the 
schema checking.  See the image below of an example session.

Note each of these contain identical definitions for HAPIStatus, etc, and these must be kept in sync (and 
will presumably be #included if this can be done, or deleted) when combined into the one json document 
that the JavaScript verifier is expecting.

![image](https://github.com/hapi-server/data-specification-schema/assets/3385225/fddbd221-2080-4433-bf98-1c178af4bc6b)

