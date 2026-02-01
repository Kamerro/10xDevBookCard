$env:DATABASE_URL="postgresql+psycopg://bookcards:bookcards@localhost:5432/bookcards"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload


docker run --name bookcards-postgres `
  -e POSTGRES_USER=bookcards `
  -e POSTGRES_PASSWORD=bookcards `
  -e POSTGRES_DB=bookcards `
  -p 5432:5432 `
  -d postgres:16

docker start bookcards-postgres
$env:DATABASE_URL="postgresql+psycopg://bookcards:bookcards@localhost:5432/bookcards"
$env:SECRET_KEY="xxyyaa"

.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt


python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt


3) Migracje DB (tabele)
powershell
python -m alembic upgrade head
4) Start serwera
powershell
python -m uvicorn app.main:app --reload
5) Szybki smoke test
DB healthcheck: http://127.0.0.1:8000/health/db → {"ok": true}
Swagger: http://127.0.0.1:8000/docs
UI: http://127.0.0.1:8000/login

# ========================================
# TESTY (pytest)
# ========================================

# Wymagana testowa baza danych (jednorazowo):
docker exec -it bookcards-postgres psql -U bookcards -c "CREATE DATABASE bookcards_test;"

# Uruchom wszystkie testy:
python -m pytest

# Tylko testy P0 (smoke):
python -m pytest -m p0

# Tylko testy P1:
python -m pytest -m p1

# Konkretny plik:
python -m pytest tests/test_auth_api.py

# Z verbose output:
python -m pytest -v

# Z coverage (wymaga pytest-cov):
python -m pytest --cov=app --cov-report=term-missing

$env:OPENROUTER_API_KEY="..."