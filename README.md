# IT Service Governance & Reporting Suite

An end-to-end SLA/KPI governance reporting project simulating the reporting function of a Business Reporting & Governance team — the kind of work behind Accenture's Measurement & Reporting associate role (Incident Management, Change Management, and Survey Management, rolled into unified SLA/KPI reporting).

## Project Overview

Most portfolio projects show one dataset and one dashboard. This project simulates three **linked** operational streams the way a real governance function tracks them together — because SLA performance, change reliability, and customer satisfaction aren't independent; they drive each other.

| Stream | What it tracks | Volume |
|---|---|---|
| **Incident Management** | Helpdesk tickets, priority (P1–P4), SLA target vs. actual resolution time | 1,200 tickets |
| **Change Management** | Change requests, approval turnaround, risk level, success/failure outcome | 250 changes |
| **Survey Management (CSAT)** | Post-resolution satisfaction score (1–5), linked to the originating ticket | 780 responses |

## Key Finding

**Breached SLAs cost an average of 1.64 points of customer satisfaction** (4.33 CSAT when met vs. 2.69 when breached) — the single insight that ties all three streams into one governance story.

## Tools & Techniques

- **Excel**: formula-driven SLA logic (not hardcoded) — `IF`, `COUNTIFS`, `AVERAGEIFS`, `INDEX/MATCH` — with a built-in validation column that independently re-derives every ticket's Met/Breached status and cross-checks it against the source data
- **Power BI**: full data model with relationships, DAX measures (`_Measures` table pattern), 8 distinct visual types (KPI cards, gauge, donut, treemap, line, bar, matrix with conditional formatting), 3 working slicers, and a custom brand theme
- **Power Query**: parameterized data source (`FilePath` parameter) so the report isn't hardcoded to one machine's file path — a step toward production-ready automation
- **PowerPoint**: a 6-slide Monthly Governance Review deck summarizing findings and recommended actions for a leadership audience

## Automation & Governance Story

The reporting layer is built so that new data flows through without manual rework:
- Formulas recalculate automatically — no pivot table needs manual refreshing
- The Power BI model refreshes from source with one click, with all measures/visuals updating automatically
- The file path is parameterized, so moving the source file doesn't break the report
- In a production environment with Power BI Service access, this would run on a nightly **scheduled refresh** — the architecture is already built for it

## Report Artifacts

Beyond the dashboard, the project includes the actual report *outputs* a governance associate would publish:
- **Daily Flash Report** — same-day ticket volume and P1 breach snapshot
- **Weekly Trend Report** — 7-day SLA compliance and top breach category
- **Ad-hoc Report Example** — a leadership question ("are high-risk changes failing more often?") answered on demand

## Files in this Repository

- `incidents.csv`, `changes.csv`, `surveys.csv` — the three linked source datasets
- `SLA_KPI_Governance_Tracker.xlsx` — Excel workbook with formula-driven SLA logic, KPI summary, and report artifacts
- `governance_theme.json` — custom Power BI theme file
- `Monthly_Governance_Review.pptx` — executive summary deck
- *(Power BI .pbix file to be added — built and maintained locally in Power BI Desktop)*

## Why This Project

Built to demonstrate the specific skill set behind Business Reporting & Governance roles: publishing accurate recurring reports on a cadence, supporting ad-hoc requests, and identifying automation opportunities — using contractual SLA/KPI tracking across Incident, Change, and Survey Management, the way a real governance function operates.
