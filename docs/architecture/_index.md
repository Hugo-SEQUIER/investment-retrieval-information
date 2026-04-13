# Architecture Index

## Purpose
- Routing map for architecture-level references.

## Components
| Component | Boundary | Primary Doc | Notes |
|---|---|---|---|
| Fetch layer | External sources -> normalized raw posts | `docs/features/social-discovery/README.md` | Uses Scweet and PRAW |
| Filter layer | Raw posts -> kept/discarded with reasons | `docs/features/content-filtering/README.md` | Cheap-model gate + dedup |
| Analysis layer | Filtered posts -> ticker/theme claims and follow-ups | `docs/features/ticker-analysis/README.md` | Includes optional web research |
| Reporting layer | Analyzed items -> concise daily digest | `docs/features/digest-reporting/README.md` | Markdown canonical output |
| Memory layer | Report + analyzed claims -> Obsidian notes | `docs/features/obsidian-memory/README.md` | Overwrite policy for managed sections |
| Daily pipeline orchestrator | Coordinates stage execution and lifecycle updates | `docs/features/daily-pipeline/README.md` | Strict stage order + status instrumentation |
| Persistence layer | Stores run state, stage status, source health, and reports | `docs/features/persistence-run-state/README.md` | SQLite-backed observability and payload storage |

## Cross-Cutting
- Decisions: `docs/decision-index.md`
- Feature mapping: `docs/feature-map.md`

## Maintenance
- Last reviewed: 2026-04-13
- Update trigger: architecture boundary changes
