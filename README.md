# Cross-System Reconciliation & Tenant Isolation

A full-stack reconciliation application built for the AdosX Full-Stack Engineer assessment.

The application imports two independent system exports, handles deliberately dirty data, matches records across the systems, identifies discrepancies, enforces tenant boundaries, and displays the results through a React dashboard.

## Tech Stack

### Backend

* Python
* Django
* Django REST Framework
* SQLite

### Frontend

* React
* Vite
* Axios

### Testing

* Django `TestCase`
* Django REST Framework `APIClient`

---

# What I Built

## 1. CSV Ingestion

The application imports:

* `locations.csv`
* `system_a.csv`
* `system_b.csv`

The location table is loaded first because it is the source of truth for mapping locations to organizations.

The importer uses defensive parsing for dates and decimal values so malformed values do not crash the import.

For example:

* blank numeric values become `None`
* invalid numeric values such as `########` become `None`
* original System B references are preserved
* dirty references are normalized only during reconciliation

The imported dataset currently contains:

* 5 locations
* 120 System A records
* 121 System B entries

The extra System B entry is expected because the dataset contains duplicate entries.

## 2. Reconciliation

The comparison logic is separated into:

`backend/reconciler/services/comparator.py`

System B entries are grouped using a normalized version of `record_ref`.

The reconciliation detects:

* `MISSING_IN_SYSTEM_B`
* `ORPHAN_IN_SYSTEM_B`
* `DUPLICATE_IN_SYSTEM_B`
* `VALUE_MISMATCH`

Reference normalization handles different representations such as:

```text
REC-1112
1112
REC 1112
```

The original database value is not modified.

## 3. Tenant Isolation

Tenant ownership comes from the `Location` model:

```text
Location → org_id
```

The API requires an `org_id` query parameter.

Example:

```text
/api/discrepancies/?org_id=ORG-A
```

The backend filters System A and System B data using the location's organization before returning discrepancies.

Requests without `org_id` are rejected with HTTP 400.

This means the frontend cannot simply hide another organization's data; the backend itself scopes the reconciliation.

## 4. React Dashboard

The frontend provides:

* Organization selector
* Discrepancy reason filter
* Sorting by System A or System B value
* Summary cards
* Discrepancy table
* Location information
* Both system values
* Discrepancy reason

The UI intentionally uses simple styling because the assignment prioritizes correctness and functionality over visual design.

---

# Project Structure

```text
cross-system-reconciliation/

├── backend/
│   ├── manage.py
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── reconciler/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_data.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services/
│   │   │   └── comparator.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── system_a.csv
│   ├── system_b.csv
│   └── locations.csv
│
├── DECISIONS.md
├── README.md
└── .gitignore
```

Django-generated files such as `admin.py`, `apps.py`, `asgi.py`, migration files, and `__init__.py` are included in the project but are not individually listed above because they are standard framework files.

---

# Running Locally

## Prerequisites

* Python 3.11+
* Node.js 18+
* npm

## 1. Clone the Repository

```bash
git clone https://github.com/SainikithaSingireddy/cross-system-reconciliation-engine
cd cross-system-reconciliation
```

## 2. Backend Setup

Open a terminal:

```bash
cd backend
```

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Import the CSV data:

```bash
python manage.py import_data
```

Start Django:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## 3. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start Vite:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173/
```

---

# API

## Get Discrepancies

```text
GET /api/discrepancies/?org_id=ORG-A
```

## Filter by Reason

```text
GET /api/discrepancies/?org_id=ORG-A&reason=VALUE_MISMATCH
```

## Sort by System A Value

```text
GET /api/discrepancies/?org_id=ORG-A&ordering=-system_a
```

## Sort by System B Value

```text
GET /api/discrepancies/?org_id=ORG-A&ordering=-system_b
```

An `org_id` is mandatory.

Example response:

```json
{
  "org_id": "ORG-A",
  "count": 8,
  "results": []
}
```

---

# Tests

The reconciliation tests cover the important decision logic:

* Record missing from System B
* Orphan System B record
* Duplicate System B entries
* Value mismatch
* Dirty reference normalization
* Invalid System B numeric value
* Tenant isolation
* API tenant requirement
* API tenant isolation

Run:

```bash
cd backend
python manage.py test
```

Current result:

```text
Ran 10 tests

OK
```

---

# What I Deliberately Did Not Build

The assignment explicitly says not to spend time on areas that are outside the core problem, so I intentionally kept the scope small.

I did not build:

* Authentication or user accounts
* Role-based access control
* Multi-database tenant routing
* Background job processing
* Pagination
* Complex frontend styling
* A separate persisted discrepancy table
* Large-scale performance optimizations
* Production monitoring
* Export functionality

The dataset is small, so the reconciliation is performed on demand rather than introducing unnecessary background processing.

---

# Handling the Dirty Data

The importer is designed to continue when individual values are malformed.

Examples from the provided data include:

* blank values
* invalid numeric values such as `########`
* dirty System B references
* an orphan reference
* duplicate System B entries

The important principle is that an invalid field should not cause the entire CSV row to disappear.

For example, the imported `REC-1064` System B row remains in the database even though its numeric value cannot be parsed.

Likewise, the orphan `REC-1999` entry remains available for reconciliation and is reported as:

```text
ORPHAN_IN_SYSTEM_B
```

---

# How I Worked With the Agent

I used an AI coding agent as a development assistant rather than treating its output as automatically correct.

My workflow was:

1. Break the assignment into ingestion, models, comparison logic, API, frontend, tests, and documentation.
2. Use the agent to help generate and explain implementation pieces.
3. Run the application and tests after each meaningful change.
4. Inspect actual imported database values rather than assuming the importer worked.
5. Check the API responses for each tenant.
6. Verify dirty references against the supplied CSV data.
7. Commit working checkpoints instead of waiting until the end.

The agent was useful for quickly creating the initial Django and React structure, but I treated its suggestions as something to verify.

---

# AI Agent Blindspot

## a. One thing the AI agent got wrong. How did you notice?

One issue was around null handling in the comparison response.

The comparison code initially converted every value using `str()`. That meant a missing System B value became the string `"None"` rather than an actual JSON `null`.

I noticed this while writing the regression test for the deliberately invalid `########` value. The test exposed that the API representation was different from the intended data meaning.

I changed the comparison output so an actual missing value remains `None`, which Django REST Framework serializes as JSON `null`.

This was a useful reminder that code can appear to work while still representing data incorrectly.

---

# Least Confident Part

## b. Which part of the submission are you least confident about, and why?

The part I am least confident about is reference normalization.

The supplied dataset contains a small number of known reference formats, so the current normalization handles those formats without adding complicated heuristics.

Real production exports could contain additional formats that are not represented in this dataset. I would want more examples from the source systems before making the normalization rules more aggressive, because incorrectly matching two different records would be worse than reporting a possible orphan.

---

# Second-Day Priority

## c. If you had a second day, what would you fix first?

I would improve the ingestion and auditability layer first.

Specifically, I would preserve raw imported values alongside normalized values and add an import report showing:

* total rows read
* rows successfully parsed
* fields that could not be parsed
* orphan references
* duplicate references
* rows requiring normalization

This would make the ingestion process easier to audit and would give users more visibility into why a particular discrepancy was produced.

After that, I would add a small export feature for the discrepancy results.

---

# Scope

The goal of this submission was to deliver a small, complete, understandable slice of the problem rather than attempt every possible production feature.

The core flow is complete:

```text
CSV files
   ↓
Django importer
   ↓
SQLite database
   ↓
Tenant-scoped reconciliation service
   ↓
Django REST API
   ↓
React dashboard
```

The implementation prioritizes correctness, dirty-data handling, tenant isolation, tests, and explainable design decisions.
