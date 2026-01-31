# Decision 0001 — Layering: web/api vs services vs models

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](../GOVERNANCE.md)
> - [PRD](../prd.md)

## Status

Accepted

## Context

Projekt łączy SSR (Jinja2) oraz JSON API. Bez jasnych granic logika zaczyna się dublować i rozjeżdżać.

## Decision

- SSR routes żyją w `app/web/*`.
- API routes żyją w `app/api/*`.
- Logika biznesowa żyje w `app/services/*`.
- Modele DB w `app/models/*`, session w `app/db/*`.

Routes mają być cienkie: auth + walidacja + orchestration + delegacja do serwisów.

## Consequences

- Unikamy dublowania logiki między SSR i API.
- Serwisy są testowalne bez FastAPI Request/Response.
