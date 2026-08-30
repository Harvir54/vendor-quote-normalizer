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
quote-normalizer sample-data/quotes/synthetic-painting-estimate-blue-oak.pdf
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Next step

Convert extracted text into the structured comparison schema and evaluate it
against the records in `sample-data/ground-truth/`.
