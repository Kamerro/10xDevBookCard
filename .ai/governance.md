# GOVERNANCE — BookCards (Release 1.0)

> **Najważniejsze dokumenty (AI + Product)**
> - [GOVERNANCE](./governance.md)
> - [PRD](../01-product/prd.md)

## Meta

- **Governance Version:** 1.0.0
- **Release:** 1.0
- **Scope:** zasady dla zmian w tym repo (bez refactoru struktury teraz)
- **Status:** Active

## Cel

Ten dokument jest **najważniejszym kontraktem** dla prac nad repo. Każda zmiana (fix/update/feature) ma:

- respektować poniższe zasady
- aktualizować ten dokument, jeśli dotyczy architektury, flow, bezpieczeństwa lub standardów

## Architektura — stan obowiązujący

### Warstwy

- **Transport (SSR):** `app/web/*` (FastAPI routes + render Jinja2)
- **Transport (API):** `app/api/*` (FastAPI JSON routes)
- **Domena / logika biznesowa:** `app/services/*`
- **Dane:** `app/models/*`, `app/db/*`
- **UI:** `templates/*` + `static/*`
- **Migracje:** `alembic/*`

### Zasada nadrzędna

- **Routes są cienkie** (walidacja, autoryzacja, przekazanie do serwisu, zwrot odpowiedzi)
- **Serwisy są grube** (większość logiki; bez zależności od FastAPI Request/Response)

## Zasady (Do / Don’t)

### Nie wolno

- Nie commitować sekretów (API keys, tokeny, hasła). W repo tylko `.env.example` i placeholdery.
- Nie zmieniać schematu DB bez migracji Alembic.
- Nie umieszczać logiki biznesowej w routerach (`app/web`, `app/api`).
- Nie dublować logiki między SSR i API — logika ma żyć w `app/services`.
- Nie wykonywać calli do LLM “na skróty” — integracja z AI tylko przez `app/services/openrouter_service.py` i orkiestrację w `app/services/ai_service.py`.
- Nie łamać kontraktów auth:
  - SSR: cookie (HttpOnly)
  - API: bearer token
- Nie wprowadzać zmian “UI flow invariants” bez aktualizacji testów i doc:
  - `/` to public landing
  - login/register redirect -> `/books`

### Zalecane

- Zmiana w logice = test (`pytest`).
- Każda większa decyzja architektoniczna powinna trafić do sekcji `Changelog` (min. wpis).

## AI — zasady integracji

- Trigger AI po dodaniu/edycji notatki jest asynchroniczny (`BackgroundTasks`).
- W DB obowiązuje mechanizm koalescencji i kontroli wyścigów:
  - `analysis_version`
  - `requested_version`
- UI ma komunikować status (`processing/ready/failed`) i wyświetlać `summary` gdy gotowe.

## Testy

- Framework: `pytest`
- Cel CI (na ten etap): unit + integration bez zewnętrznych serwisów i bez odpalania DB kontenerowej.

## Bezpieczeństwo i CI/CD

- Obowiązuje pipeline z `.github/workflows/*` oraz plan w `.ai/05-security/cicd-security-plan.md`.
- Lint/format: `ruff`.
- SAST: CodeQL.
- Dependency audit: `pip-audit`.

## Wersjonowanie dokumentu

- Dokument jest wersjonowany SemVer:
  - **PATCH**: doprecyzowanie zasad bez zmiany kierunku
  - **MINOR**: nowa zasada/proces, kompatybilny ze starym
  - **MAJOR**: breaking change w zasadach (np. refactor warstw, nowy sposób auth, zmiana kontraktu AI)

## Kiedy trzeba zaktualizować GOVERNANCE

Zaktualizuj ten plik, jeśli zmiana dotyczy:

- struktury folderów / odpowiedzialności modułów
- auth flow / cookies / tokenów
- modeli DB / migracji
- AI pipeline (trigger, statusy, schema, prompt, concurrency)
- CI/CD, security scanning, narzędzi jakości
- kluczowych invariantów UX (routing/redirecty)

## Changelog

### 1.0.0

- Initial governance dla Release 1.0
