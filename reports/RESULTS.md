# Reconciliation results

## June 2026 control summary

| Metric | Result |
|---|---:|
| Bank transactions | 2,039 |
| Ledger transactions reviewed | 2,320 |
| Matched transactions | 2,035 |
| Bank-side exceptions | 4 |
| Ledger-side exceptions | 285 |
| Bank-side match rate | 99.8% |
| Maximum matched date difference | 4 days |
| Duplicate reuse of bank or GL rows | 0 |

All 2,035 matches were produced by the strictest rule: normalized reference
plus exact amount. The broader timing and description rules remain available
for less standardized future inputs and are covered by automated tests.

## Bank-side exceptions identified

| Reference | Description | Amount |
|---|---|---:|
| BKF-0605 | Monthly account-maintenance fee | ($35.00) |
| ACH-RET-0612 | Returned customer ACH | ($2,951.30) |
| WIRE-0618 | Domestic wire-processing fee | ($45.00) |
| INT-0630 | Monthly interest credit | $842.17 |

The four exceptions total a net **($2,189.13)** and were deliberately added to
the simulated external statement. In a real close, they would require review
and potentially adjusting journal entries.

## Ledger-side exceptions

The 285 ledger-side items are entries posted by June 30 that did not appear on
the June statement within the selected population. They are candidates for
outstanding checks, deposits in transit, timing differences, or investigation.
They are not automatically classified as errors.

## Interpretation limits

This is a synthetic control exercise. Results demonstrate a reproducible
reconciliation process and should not be interpreted as real operational
savings, audit conclusions, or performance claims.

