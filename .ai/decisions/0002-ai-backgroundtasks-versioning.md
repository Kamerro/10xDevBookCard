# Decision 0002 — AI: BackgroundTasks + DB versioning (analysis_version/requested_version)

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](../GOVERNANCE.md)
> - [PRD](../prd.md)

## Status

Accepted

## Context

AI analiza notatek nie może blokować requestów SSR/API. Jednocześnie szybkie edycje notatek nie mogą powodować wielu równoległych analiz i nadpisywania nowszych wyników starszymi.

## Decision

- Analiza AI jest odpalana asynchronicznie przez FastAPI `BackgroundTasks`.
- Rekord `BookAIAnalysis` utrzymuje koalescencję i kontrolę wyścigów przez pola:
  - `analysis_version`
  - `requested_version`

W skrócie: endpointy podbijają `requested_version`, a worker zapisuje wynik tylko jeśli analizowana wersja jest nadal aktualna.

## Consequences

- Nie blokujemy request lifecycle.
- Unikamy dublowania calli do OpenRouter.
- Wynik AI jest zawsze spójny z najnowszym stanem notatek.
