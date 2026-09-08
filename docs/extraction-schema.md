# Contractor Estimate Extraction Schema

## Goal

Turn differently formatted contractor estimates into consistent records that a
property manager can compare without assuming that missing language means work
is included.

## Status values

Every comparison item uses one of four statuses:

- `included`: the estimate explicitly includes the work or term.
- `excluded`: the estimate explicitly says it is not included.
- `not_stated`: the estimate does not address it.
- `unclear`: relevant language exists, but its meaning or price is conditional.

## Record shape

Each normalized estimate contains:

- `document`: fixture ID, source filename, synthetic flag, and document type.
- `vendor`: company name and contact details exactly as written.
- `project`: customer, address, property type, occupancy, bedrooms, bathrooms,
  approximate square footage, and trade.
- `estimate`: estimate number, dates, total, tax, deposit, timeline, and warranty.
- `scope_items`: normalized comparison categories with a status, price when it is
  separately stated, evidence copied from the document, and explanatory notes.
- `line_items`: the contractor's original priced rows.
- `exclusions`: explicit exclusions in the document.
- `risk_flags`: facts a reviewer should resolve before accepting the estimate.

## Initial painting categories

The first version compares these categories:

1. Surface protection
2. Drywall repair
3. Primer or stain blocking
4. Walls
5. Wall coat count
6. Ceilings
7. Baseboards and door casings
8. Interior doors
9. Paint and materials
10. Cleanup
11. Debris disposal
12. Labor warranty

## Extraction rules

1. Preserve the quoted total; do not recalculate or silently correct it.
2. Store money as integer cents.
3. Record only facts supported by document evidence.
4. Do not turn `not_stated` into `excluded`.
5. Keep allowances and conditional work visible as risk flags.
6. Never use outside knowledge to fill missing estimate terms.
7. A human-readable explanation should accompany each comparison warning.

## Success criteria for the first prototype

For both fixtures, the extractor should correctly capture the vendor, address,
total, deposit, duration, all 12 comparison categories, and every risk flag. A
field counts as correct only when both its value and status match the manually
verified ground truth.

## Additional trade profiles

The current application also uses dedicated schemas for flooring, plumbing,
and HVAC. Each profile defines its own comparison rows, risk-worthy omissions,
and technical details. Shared bid metadata—such as proposal number, dates,
license, schedule, payment terms, and exclusions—uses the same structure in
all four categories.
