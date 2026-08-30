# Vendor Quote Normalizer

An AI-assisted application that helps property managers compare contractor estimates consistently and identify differences in price, scope, exclusions, and risk.

## Structure

- `app/` — application source code
- `docs/` — product requirements and architecture
- `sample-data/quotes/` — anonymized or synthetic contractor estimates
- `research/` — interviews, market research, and validation notes
- `tests/` — automated tests and evaluation cases

## Current status

The first trade is interior painting. Two synthetic estimates and their manually
verified ground-truth records are ready for extraction testing. The first local
prototype can extract text from digital PDF estimates.

## Run locally

Create and activate the Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Extract one sample estimate:

```bash
python -m app.cli sample-data/quotes/synthetic-painting-estimate-blue-oak.pdf
```

Produce normalized JSON instead of raw text:

```bash
python -m app.cli sample-data/quotes/synthetic-painting-estimate-blue-oak.pdf --format json
```

Compare two estimates:

```bash
python -m app.cli sample-data/quotes/synthetic-painting-estimate-blue-oak.pdf \
  --compare sample-data/quotes/synthetic-painting-estimate-inland-pro.pdf
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

Start the local API server:

```bash
python -m uvicorn app.api:app --reload
```

Then open `http://127.0.0.1:8000/docs` to test the API through FastAPI's
interactive documentation page.

## Next step

Convert extracted text into the structured comparison schema and evaluate it
against the records in `sample-data/ground-truth/`.
