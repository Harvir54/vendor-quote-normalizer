# Vendor Quote Normalizer

An evidence-first application that helps property teams compare contractor
estimates consistently and identify differences in price, scope, exclusions,
and risk. Every classification retains the contractor's original wording.

## Structure

- `app/` - Python extraction, normalization, comparison, and API code
- `frontend/` - Next.js and React user interface
- `docs/` - product requirements and architecture
- `sample-data/quotes/` - anonymized or synthetic contractor estimates
- `sample-data/ground-truth/` - human-verified expected results
- `research/` - interviews, market research, and validation notes
- `tests/` - automated tests and evaluation cases

## Current status

The prototype supports interior painting, flooring, and plumbing with a
different comparison profile for each trade. Synthetic demo estimates are
included for every category. The application extracts digital PDF text and,
when the optional API key is configured, transcribes scanned PDFs with AI,
normalizes trade-specific scope, compares two to five estimates, and displays
evidence-backed risks in a web interface. Low-confidence wording can be
interpreted by an optional, evidence-validated AI fallback.

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- pnpm

Confirm they are available:

```bash
python3 --version
node --version
pnpm --version
```

## First-time setup

Create and activate the Python environment:

```bash
make setup
```

## Run the web application

Start the API in the first terminal:

```bash
make api
```

Start the frontend in a second terminal:

```bash
make web
```

Open `http://localhost:3000`. Keep both terminals running while using the app.

FastAPI's interactive API documentation is available at
`http://127.0.0.1:8000/docs`.

## Optional AI fallback

The backend uses deterministic rules first. When a result is marked for review
and `OPENAI_API_KEY` is available, it sends the flagged categories to OpenAI's
Responses API using a strict structured-output schema. Model evidence must be
an exact quote from the extracted PDF text before the result is accepted.

The same key enables OCR for image-only PDFs. Digital PDFs are still processed
locally first, so OCR is not called or billed unless no text layer is found.
Scanned documents are limited to 10 pages to control cost. You can set
`OPENAI_OCR_MODEL` separately; otherwise OCR uses `OPENAI_MODEL`.

Set the key in the same terminal used to start the API:

```bash
export OPENAI_API_KEY="your-key-here"
make api
```

Never place the key in frontend code or commit it to Git. The `/health`
endpoint reports `ai_enabled` without exposing the key.

## Developer commands

Run all backend tests:

```bash
make test
```

Check frontend code quality:

```bash
make lint
```

Create a production frontend build:

```bash
make build
```

## Command-line usage

Extract one sample estimate:

```bash
.venv/bin/python -m app.cli sample-data/quotes/synthetic-painting-estimate-blue-oak.pdf
```

Produce normalized JSON instead of raw text:

```bash
.venv/bin/python -m app.cli sample-data/quotes/synthetic-painting-estimate-blue-oak.pdf --format json
```

Compare two estimates:

```bash
.venv/bin/python -m app.cli sample-data/quotes/synthetic-painting-estimate-blue-oak.pdf \
  --compare sample-data/quotes/synthetic-painting-estimate-inland-pro.pdf
```

Choose a different trade with `--trade flooring` or `--trade plumbing`.

## Current limitations

- Scanned image-only PDFs require `OPENAI_API_KEY` and are limited to 10 pages.
- The current trade profiles cover interior painting, flooring, and plumbing.
- Each comparison accepts between two and five estimates.
