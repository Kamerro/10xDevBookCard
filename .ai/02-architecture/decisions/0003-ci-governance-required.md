# Decision 0003 — CI requires .ai/GOVERNANCE.md

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](../GOVERNANCE.md)
> - [PRD](../prd.md)

## Status

Accepted

## Context

Projekt ma być rozwijany przez ludzi i agentów AI. Bez twardego punktu odniesienia zasady szybko się rozjadą.

## Decision

- CI zawiera job `Governance Check`, który:
  - wymaga istnienia `.ai/GOVERNANCE.md`
  - wymaga nagłówka `**Governance Version:**`
  - drukuje początek pliku w logach

## Consequences

- Każdy PR ma widoczny kontekst zasad.
- Brak lub uszkodzenie governance blokuje pipeline.
