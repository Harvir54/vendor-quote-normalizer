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
- `sample-data/evaluation/` - curated cross-trade wording and edge cases
- `sample-data/public-validation/` - anonymized excerpts from cited public bid records
- `research/` - interviews, market research, and validation notes
- `tests/` - automated tests and evaluation cases

## Current status

The prototype supports interior painting, flooring, plumbing, and HVAC with a
different comparison profile for each trade. Synthetic demo estimates are
included for every category. The application accepts PDF, JPG, JPEG, PNG,
HEIC, and HEIF estimates. It extracts digital PDF text locally and, when the
optional API key is configured, transcribes scanned PDFs and images with AI,
normalizes trade-specific scope, compares two to five estimates, and displays
evidence-backed risks in a web interface. Low-confidence wording can be
interpreted by an optional, evidence-validated AI fallback.

Every trade also extracts a compact set of shared bid details when stated:
proposal number, issue date, validity, contractor license, project schedule,
payment terms, and exclusions. These stay collapsed in the interface until a
user chooses to review them.

Painting comparisons also evaluate surface preparation, protection of floors
and fixed property, trim and doors, stated paint manufacturer/product/sheen,
and lead-safety language. Secondary specifications remain collapsed by default
so the main scope comparison stays concise.

Flooring comparisons additionally retain the stated installation method,
material-order quantity and waste allowance, moisture testing, acclimation,
and responsibility for moving furniture, appliances, or toilets. These
secondary installation details are collapsed by default.

Plumbing comparisons identify fixture replacement, water-heater, repipe,
sewer or drain replacement, leak-repair, and drain-cleaning work so unrelated
bids are not presented as equivalent. When applicable, they also retain
water-heater specifications, old-equipment removal, access restoration,
camera inspection, and excavation details. Unused technical rows stay hidden.

HVAC comparisons evaluate system configuration, capacity, current efficiency
ratings, equipment models, ductwork, controls, permits, commissioning, removal,
and warranty. They also surface load calculations, AHRI matched-system
documentation, electrical work, refrigerant lines, and condensate protection
when those details are stated, while keeping that technical layer collapsed.

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

The same key enables OCR for image-only PDFs and image uploads. Digital PDFs
are still processed locally first, so OCR is not called or billed unless no
text layer is found. Scanned PDFs are limited to 10 pages, PDFs to 10 MB, and
images to 8 MB to control cost. HEIC and HEIF files are converted to JPEG in
the backend before OCR. You can set `OPENAI_OCR_MODEL` separately; otherwise
OCR uses `OPENAI_MODEL`.

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

Measure curated extraction accuracy overall and by trade:

```bash
make evaluate
```

The evaluator checks every expected field value, reports any failure with its
case ID and actual value, and exits unsuccessfully when a regression is found.
Use `.venv/bin/python -m scripts.evaluate_accuracy --json` for machine-readable
results.

Run the separate public-source validation set with `make evaluate-public`.
These records come from government bid tabulations and retain source URLs and
access dates, but remove contractor and staff identities. Because bid tabs
usually omit detailed scope, they validate public-document layouts and pricing
labels rather than the full residential scope schema.

Check frontend code quality:

```bash
make lint
```

Create a production frontend build:

```bash
make build
```

## Reviewing and correcting results

After a comparison, choose **Correct results** to override a scope status, add
the corrected detail, and optionally record why it was changed. Corrected
cells are marked as human verified and are included in printed and downloaded
reports. Corrections currently live in the browser for that comparison; they
are not saved to a database or used to train a model. The clarification flags
continue to reflect the original extraction.

Two image fixtures are included in `sample-data/quotes/` for manual upload
testing. Image OCR requires a configured API key and can incur model usage.

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

Choose a different trade with `--trade flooring`, `--trade plumbing`, or
`--trade hvac`.

## Current limitations

- Scanned PDFs and image uploads require `OPENAI_API_KEY`; direct images are
  currently limited to one estimate image per vendor upload.
- The current trade profiles cover interior painting, flooring, plumbing, and HVAC.
- Each comparison accepts between two and five estimates.
