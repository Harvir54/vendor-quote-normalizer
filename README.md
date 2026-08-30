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
verified ground-truth records are ready for extraction testing.

## Next step

Build the first PDF text-extraction prototype and compare its output with the
ground-truth records in `sample-data/ground-truth/`.
