# Trace contract

The models in `risansym.schemas` are the advanced API for consumers that read
or validate trace files. They are deliberately not re-exported from the
package root.

`TraceOutput` is the authoritative Pydantic model for schema version `1.0`.
The generated JSON Schema lives at `shared/schema/trace.schema.json`.
Compatible additions require optional fields. Any change that alters required
fields or their meaning must introduce a new `schema_version` and update both
validators and shared fixtures in the same delivery.

::: risansym.schemas
