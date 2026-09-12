# Architectural Decisions

## 1. Database: SQLite

* **Decision:** Use SQLite as the application database.
* **Alternative:** PostgreSQL.
* **Reasoning:** The assignment contains only 120 rows per source, so SQLite keeps the project simple while still providing persistent relational storage.

## 2. Separate models for System A and System B

* **Decision:** Store System A records and System B entries in separate database tables.
* **Alternative:** Merge both sources into one generic events table.
* **Reasoning:** The two exports have different structures and semantics, and keeping them separate makes the reconciliation logic easier to understand and audit.

## 3. Keep dirty references as imported

* **Decision:** Store the original `record_ref` from System B and normalize it only when matching.
* **Alternative:** Replace the original reference with a cleaned value during import.
* **Reasoning:** Keeping the original value preserves the source data for auditing while allowing deterministic matching.

## 4. Defensive numeric parsing

* **Decision:** Convert valid numeric values to `Decimal` and represent invalid or blank values as `None`.
* **Alternative:** Reject the entire row when a numeric field cannot be parsed.
* **Reasoning:** The assignment explicitly requires malformed rows to survive ingestion rather than being silently dropped.

## 5. Python reconciliation service

* **Decision:** Put comparison logic in a dedicated Python service using normalized-reference mappings.
* **Alternative:** Implement the reconciliation entirely with complex SQL joins.
* **Reasoning:** The dataset is small, and a Python service is easier to read, test, and modify for the deliberately dirty references.

## 6. Mandatory tenant scope in the API

* **Decision:** Require `org_id` for every discrepancy API request and filter records by the location's organization.
* **Alternative:** Provide an unscoped endpoint and rely on the frontend organization selector.
* **Reasoning:** Tenant isolation must be enforced by the backend and must not depend on the frontend hiding another tenant's data.

## 7. On-demand reconciliation

* **Decision:** Calculate discrepancies when the API endpoint is requested.
* **Alternative:** Store a separate discrepancy table and periodically precompute results.
* **Reasoning:** With only 120 records per source, on-demand comparison is simple enough and avoids maintaining a second source of truth.

## 8. Plain React UI

* **Decision:** Use a small React/Vite dashboard with inline styling and native controls.
* **Alternative:** Add a UI component library and spend more time on visual design.
* **Reasoning:** The assignment explicitly prioritizes a working reconciliation screen over visual polish.
