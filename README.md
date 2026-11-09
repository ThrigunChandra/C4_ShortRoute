# ShortRoute

ShortRoute is a FastAPI backend for creating, managing, and redirecting short URLs. It supports visitor links, authenticated users, permanent member links, premium custom aliases, session-based authentication, Redis caching, click tracking, and request rate limiting.

## Features

- Create eight-character short URLs
- Visitor links expire after 30 days
- Logged-in users receive permanent links
- Premium users can create aliases such as `/username/portfolio`
- Register, log in, view the current account, and log out
- Server-side sessions stored in PostgreSQL with hashed session tokens
- `HttpOnly` session cookies
- List, inspect, and delete links owned by the logged-in user
- Ownership checks prevent users from managing another user's links
- Click counting for owned links
- Redis cache-aside handling for short-code and custom-alias redirects
- Fixed-window Redis rate limiting for link creation
- PostgreSQL constraints for unique codes, aliases, usernames, and emails
- Automated tests with pytest

## Stack

- Python and FastAPI
- PostgreSQL and SQLAlchemy
- Redis
- Argon2 password hashing
- Docker Compose
- pytest

## Project structure

```text
app/
├── database/       # PostgreSQL and Redis clients
├── dependencies/   # Authentication and rate-limit dependencies
├── models/         # SQLAlchemy models
├── routes/
│   ├── auth/       # Registration, login, account, and logout
│   ├── links/      # Link creation and management
│   └── redirects/  # Short-code and custom-alias redirects
├── schemas/        # Pydantic request and response schemas
├── scripts/        # Expired and revoked session cleanup
└── services/       # Hashing, caching, redirects, and rate limiting

tests/
├── auth_tests/
└── link_tests/

docker-compose.yaml # Local PostgreSQL and Redis services
requirements.txt    # Python dependencies
schema.sql          # PostgreSQL tables, constraints, and indexes
```

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/ThrigunChandra/C4_ShortRoute.git
cd C4_ShortRoute
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start PostgreSQL and Redis

```bash
docker compose up -d db redis
```

The included Compose configuration starts PostgreSQL on port `5432` and Redis on port `6379`.

### 5. Initialize the databases

Create the test database the first time you set up the project:

```bash
docker compose exec db createdb -U thrig onetwo_test
```

If `onetwo_test` already exists, skip that command. Apply the schema to both databases:

```bash
docker compose exec -T db psql -U thrig -d onetwo < schema.sql
docker compose exec -T db psql -U thrig -d onetwo_test < schema.sql
```

The schema creates the `users`, `sessions`, and `links` tables together with their constraints and indexes.

### 6. Configure environment variables

Create a `.env` file in the project root:

```dotenv
DATABASE_URL=postgresql+psycopg://thrig:local_password@127.0.0.1:5432/onetwo
TEST_DATABASE_URL=postgresql+psycopg://thrig:local_password@127.0.0.1:5432/onetwo_test
REDIS_URL=redis://127.0.0.1:6379/0
```

These credentials are only for the local Docker Compose environment. Use secure credentials when deploying the application.

### 7. Run the API

```bash
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/auth/register` | Register an account |
| `POST` | `/auth/login` | Log in and create a session |
| `GET` | `/auth/me` | Return the logged-in user |
| `POST` | `/auth/logout` | Revoke the current session |
| `POST` | `/api/links` | Create a short link |
| `GET` | `/api/links` | List the current user's links |
| `GET` | `/api/links/{link_id}` | View an owned link |
| `DELETE` | `/api/links/{link_id}` | Delete an owned link |
| `GET` | `/{short_code}` | Redirect through a short code |
| `GET` | `/{username}/{custom_slug}` | Redirect through a premium alias |

## Rate limits

Link creation uses a 60-second fixed window stored in Redis:

| Caller | Requests per window | Identity |
|---|---:|---|
| Visitor | 5 | IP address |
| Free user | 10 | User ID |
| Premium user | 30 | User ID |

Exceeding the limit returns `429 Too Many Requests` with a `Retry-After` header. If Redis is unavailable, link creation returns `503 Service Unavailable`.

## Running tests

Start PostgreSQL and Redis, then run:

```bash
python -m pytest -q
```

The current automated suite contains 38 passing tests covering authentication, link management, redirects, custom aliases, click counting, and Redis caching. Rate limiting is currently checked manually through the interactive API documentation.

## Notes

- `.env`, `.venv`, cache directories, and editor settings are excluded from Git.
- Redis persistence is disabled in the local Compose configuration because it stores disposable cache and rate-limit data.
- PostgreSQL remains the source of truth for users, sessions, and links.
- Local session cookies use `secure=False`; deployment over HTTPS should use secure cookies.
