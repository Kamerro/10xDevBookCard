# Deployment — BookCards (Fly.io)

> **Najważniejsze dokumenty (source of truth)**
> - [GOVERNANCE](./GOVERNANCE.md)
> - [PRD](./prd.md)

## Platforma

- **Fly.io** — tani, prosty, GitHub integration
- Region: `waw` (Warszawa)
- Forma: Docker container

---

## 1. Prereq — zainstaluj Fly CLI

```bash
# macOS
brew install flyctl

# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Linux
curl -L https://fly.io/install.sh | sh
```

Zaloguj się:

```bash
fly auth login
```

---

## 2. Utwórz aplikację na Fly

```bash
fly apps create bookcards
```

> Możesz zmienić nazwę `bookcards` na inną unikalną.

---

## 3. Utwórz bazę PostgreSQL

```bash
fly postgres create --name bookcards-db --region waw
```

Podłącz bazę do aplikacji:

```bash
fly postgres attach bookcards-db --app bookcards
```

Fly automatycznie ustawi `DATABASE_URL` jako secret.

---

## 4. Ustaw sekrety

```bash
# JWT secret (wygeneruj unikalny)
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" --app bookcards

# OpenRouter API key
fly secrets set OPENROUTER_API_KEY="sk-..." --app bookcards
```

Sprawdź ustawione sekrety:

```bash
fly secrets list --app bookcards
```

---

## 5. Deploy (ręcznie)

```bash
fly deploy
```

Fly zbuduje Docker image i uruchomi aplikację.

---

## 6. Deploy (automatyczny — GitHub Actions)

### A) Uzyskaj Fly API token

```bash
fly tokens create deploy -x 999999h
```

### B) Dodaj token do GitHub Secrets

1. GitHub → repo → **Settings → Secrets and variables → Actions**
2. **New repository secret**:
   - Name: `FLY_API_TOKEN`
   - Value: (token z kroku A)

### C) Workflow

Plik `.github/workflows/deploy.yml` jest już w repo.

- **Trigger:** push do `main` lub manual (`workflow_dispatch`)
- Po każdym PUSH do main aplikacja będzie automatycznie deployowana

---

## 7. Migracje bazy danych

Po deployu uruchom migracje:

```bash
fly ssh console --app bookcards -C "alembic upgrade head"
```

Albo dodaj do Dockerfile (przed CMD):

```dockerfile
RUN alembic upgrade head
```

> **Uwaga:** Migracje w Dockerfile działają tylko jeśli baza jest dostępna w czasie buildu (zazwyczaj nie jest). Lepiej uruchamiać je ręcznie lub przez release command.

### Release command (zalecane)

Dodaj do `fly.toml`:

```toml
[deploy]
  release_command = "alembic upgrade head"
```

---

## 8. Sprawdź status

```bash
# Status aplikacji
fly status --app bookcards

# Logi
fly logs --app bookcards

# Otwórz w przeglądarce
fly open --app bookcards
```

---

## 9. Koszty

| Zasób | Free tier | Powyżej |
|-------|-----------|---------|
| VM (shared-cpu-1x) | 3 maszyny | ~$1.94/mies |
| Postgres | 1GB storage | ~$1.94/mies |
| Bandwidth | 100GB/mies | $0.02/GB |

**Dla MVP:** ~$0-5/mies

---

## 10. Checklist pre-deploy

- [ ] `fly apps create bookcards`
- [ ] `fly postgres create --name bookcards-db`
- [ ] `fly postgres attach bookcards-db --app bookcards`
- [ ] `fly secrets set SECRET_KEY="..." --app bookcards`
- [ ] `fly secrets set OPENROUTER_API_KEY="..." --app bookcards`
- [ ] `fly deploy`
- [ ] `fly ssh console -C "alembic upgrade head"`
- [ ] `fly open` → sprawdź czy działa

---

## 11. Troubleshooting

### App nie startuje

```bash
fly logs --app bookcards
```

### Brak połączenia z bazą

Sprawdź czy `DATABASE_URL` jest ustawiony:

```bash
fly secrets list --app bookcards
```

### Cold start wolny

Ustaw `min_machines_running = 1` w `fly.toml` (kosztuje więcej).

---

## 12. Usuwanie

```bash
fly apps destroy bookcards
fly postgres destroy bookcards-db
```
