# Portfolio API - End-to-End Project Flow and Full API Reference

## 1) What this project does
This is a FastAPI backend for a portfolio platform.

It supports:
- User registration and login.
- JWT access + refresh token authentication.
- Admin user management.
- CRUD for projects, skills, experiences, and resume files.
- Public profile endpoint by username.
- Redis-backed caching and rate limiting, with in-memory fallback.

---

## 2) Tech stack and tools used

Runtime and framework:
- Python 3.12
- FastAPI
- Uvicorn

Data and persistence:
- PostgreSQL via SQLAlchemy
- Alembic migrations
- Redis (optional, for cache/rate-limit; memory fallback if unavailable)

Security and auth:
- `python-jose` for JWT
- `passlib[bcrypt]` for password hashing
- Refresh token persistence in DB (`refresh_tokens` table)

Validation:
- Pydantic v2 schemas
- `email-validator`

Important local tools/commands used by this project:
- `uvicorn main:app --reload` to run API
- `alembic upgrade head` to apply migrations

---

## 3) High-level project structure

- `portfolio_api/main.py`: FastAPI app startup and router inclusion.
- `portfolio_api/app/core/`: config, auth dependencies, security, redis cache, rate limit.
- `portfolio_api/app/db/`: SQLAlchemy engine/session/base/models import.
- `portfolio_api/app/models/`: DB entities (`users`, `refresh_tokens`, portfolio domain tables).
- `portfolio_api/app/schemas/`: request/response contracts.
- `portfolio_api/app/services/`: business logic per domain.
- `portfolio_api/app/routers/`: API endpoints mapped to services.
- `portfolio_api/alembic/`: migration config and revision history.
- `portfolio_api/uploads/resumes/`: uploaded resume files storage.

---

## 4) Startup flow (request lifecycle from start)

1. API process starts in `portfolio_api/main.py`.
2. `FastAPI(title='portfolio_app', version='1.0.0')` is initialized.
3. Routers are mounted:
- `/auth`
- `/users`
- `/portfolio`
- `/public`
4. Config values are loaded from `.env` via `Settings` in `app/core/config.py`.
5. Database sessions are created per request using `get_db()` from `app/db/deps.py`.
6. For protected endpoints:
- `Authorization: Bearer <access_token>` is parsed by `HTTPBearer`.
- Token is decoded in `decode_token()`.
- `get_current_user()` validates token type, user existence, active/not-deleted status.
7. Service layer executes business logic.
8. SQLAlchemy commit/refresh is done where needed.
9. Public profile cache is invalidated on portfolio mutations.

---

## 5) Core module behavior

### 5.1 Config (`app/core/config.py`)
Key settings:
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS` (also typo fallback key: `REFREH_TOKEN_EXPIRE_DAYS`)
- `PUBLIC_PROFILE_CACHE_TTL_SECONDS` (currently default `300`)
- Login/public rate-limit thresholds and windows

### 5.2 Security (`app/core/security.py`)
- `password_hash()` hashes plaintext password with bcrypt.
- `verify_password()` verifies password against hash.
- `create_access_token()` creates JWT with `type=access` and expiry in minutes.
- `create_refresh_token()` creates JWT with `type=refresh`, `jti`, and expiry in days.
- `decode_token()` decodes JWT; returns `None` on failure.
- `hash_token()` SHA-256 hashes refresh token before DB storage.

### 5.3 Auth dependency and roles (`app/core/deps.py`)
- `get_current_user()` enforces:
- valid JWT
- token type is `access`
- user exists and not deleted
- user is active
- `require_roles()` for role-based checks.
- `require_admin` allows only admin users.

### 5.4 Rate limiting (`app/core/rate_limit.py`)
- Key format: `rl:{scope}:{ip}`.
- Uses Redis first (`INCR`, `EXPIRE`, `TTL`).
- Falls back to in-memory dict if Redis unavailable.
- Returns `429` with `Retry-After`.
- Applied on:
- `/auth/login` (`limit_login`)
- `/public/{username}` (`limit_public`)

### 5.5 Cache (`app/core/redis_client.py`)
- JSON get/set/delete wrappers:
- `cache_get_json`
- `cache_set_json`
- `cache_delete`
- Redis primary; memory fallback cache if Redis import/connection fails.

### 5.6 DB layer (`app/db/session.py`, `app/db/base.py`)
- SQLAlchemy engine from `DATABASE_URL`.
- Session factory `sessiolocal`.
- `BaseTable` shared fields:
- `id`, `is_active`, `is_deleted`
- `created_by`, `created_at`
- `modify_by`, `modify_at`
- `deleted_by`, `deleted_at`

---

## 6) Data model summary

### Users (`app/models/users.py`)
- Core identity: `name`, `username` (unique), `email_id` (unique), `password_hash`
- Status: `is_verify`, `is_active`, `is_deleted`
- Auth role: `role` (`admin`, `user`)
- Relations: refresh tokens, projects, skills, experiences, resume files

### Refresh tokens (`app/models/refresh_tokens.py`)
- `user_id`, `jti` (unique), `token_hash` (unique), `expires_at`
- Revocation tracking: `revoked_at`, `replaced_by_jti`

### Portfolio domain (`app/models/portfolio.py`)
- `Project`
- `Skill`
- `Experience`
- `ResumeFile` (stores file metadata and disk path)

---

## 7) Business flow by domain

### 7.1 Auth flow
Register:
1. Check email uniqueness.
2. Generate username from name.
3. Hash password and create user.
4. Return success message.

Login:
1. Validate email/password.
2. Enforce active + not-deleted.
3. Issue access + refresh token pair.
4. Persist refresh token hash with `jti`.

Refresh:
1. Decode refresh token and validate `type=refresh`.
2. Validate token row (`jti`, hash, expiry, not revoked).
3. Rotate token:
- revoke previous row
- create new token row
4. Return new token pair.

Logout:
1. Decode refresh token.
2. Find refresh row and mark `revoked_at`.
3. Return success message.

### 7.2 User administration flow
- Admin-only list/create/get/role-change/enable/disable endpoints.
- Change password endpoint is for authenticated current user.
- Password policy requires:
- length 8-72
- uppercase, lowercase, number, special character

### 7.3 Portfolio CRUD flow
- Owner resolution:
- default owner is current user
- admin can set `user_id` query param for another user
- non-admin cannot operate on another user
- Soft delete for records (`is_deleted=True`) except file binary deletion on disk for resume file removal.
- Any create/update/delete invalidates public profile cache for that user.

### 7.4 Public profile flow
1. `GET /public/{username}` checks cache first.
2. If cache miss:
- load active/non-deleted user
- load active/non-deleted projects, skills, experiences
3. Build response projection.
4. Cache response with TTL (`PUBLIC_PROFILE_CACHE_TTL_SECONDS`).

---

## 8) Full API list

Notes:
- Base URL from env: `PUBLIC_BASE_URL` (example: `http://localhost:8000`)
- Auth format: `Authorization: Bearer <access_token>`

### 8.1 Health/root

1. `GET /`
- Auth: no
- Purpose: basic app root handler
- Current behavior: prints `"portfolio app running"` on server side

### 8.2 Auth endpoints (`/auth`)

1. `POST /auth/register`
- Auth: no
- Body: `RegisterRequest`
- Fields: `name`, `email_id`, `password`
- Returns: success message

2. `POST /auth/verify-otp`
- Auth: no
- Body: `OTPVerifyRequest`
- Fields: `email_id`, `otp`
- Returns: placeholder message (OTP currently skipped)

3. `POST /auth/login`
- Auth: no
- Body: `LoginRequest`
- Fields: `email_id`, `password`
- Rate limit: yes (`limit_login`)
- Returns: `TokenResponse`

4. `POST /auth/refresh`
- Auth: no
- Body: `RefreshTokenRequest`
- Fields: `refresh_token`
- Returns: new `TokenResponse` (refresh rotation)

5. `POST /auth/logout`
- Auth: no
- Body: `RefreshTokenRequest`
- Fields: `refresh_token`
- Returns: success message

6. `GET /auth/me`
- Auth: yes (access token)
- Returns: `AuthUserResponse`

### 8.3 User endpoints (`/users`)

1. `GET /users/me`
- Auth: yes
- Returns: `UserResponse`

2. `GET /users`
- Auth: admin only
- Query: `role`, `is_active`, `search`, `include_deleted`, `limit`, `offset`
- Returns: `UserListResponse`

3. `POST /users`
- Auth: admin only
- Body: `AdminCreateUserRequest`
- Returns: `UserResponse`

4. `PUT /users/change-password`
- Auth: yes
- Body: `ChangePasswordRequest`
- Fields: `old_password`, `new_password`
- Returns: success message

5. `GET /users/{user_id}`
- Auth: admin only
- Returns: `UserResponse`

6. `PATCH /users/{user_id}/role`
- Auth: admin only
- Body: `UserRoleUpdate`
- Returns: `UserResponse`

7. `PATCH /users/{user_id}/disable`
- Auth: admin only
- Returns: `UserResponse`

8. `PATCH /users/{user_id}/enable`
- Auth: admin only
- Returns: `UserResponse`

### 8.4 Portfolio endpoints (`/portfolio`)

Projects:
1. `POST /portfolio/projects`
2. `GET /portfolio/projects`
3. `GET /portfolio/projects/{project_id}`
4. `PUT /portfolio/projects/{project_id}`
5. `DELETE /portfolio/projects/{project_id}`
- Auth: yes
- Optional query for admin override: `user_id`
- Schemas: `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`, `ProjectListResponse`

Skills:
1. `POST /portfolio/skills`
2. `GET /portfolio/skills`
3. `GET /portfolio/skills/{skill_id}`
4. `PUT /portfolio/skills/{skill_id}`
5. `DELETE /portfolio/skills/{skill_id}`
- Auth: yes
- Optional query for admin override: `user_id`
- Schemas: `SkillCreate`, `SkillUpdate`, `SkillResponse`, `SkillListResponse`

Experiences:
1. `POST /portfolio/experiences`
2. `GET /portfolio/experiences`
3. `GET /portfolio/experiences/{experience_id}`
4. `PUT /portfolio/experiences/{experience_id}`
5. `DELETE /portfolio/experiences/{experience_id}`
- Auth: yes
- Optional query for admin override: `user_id`
- Schemas: `ExperienceCreate`, `ExperienceUpdate`, `ExperienceResponse`, `ExperienceListResponse`

Resume files:
1. `POST /portfolio/files/upload`
- Multipart upload field: `file`
2. `GET /portfolio/files`
3. `GET /portfolio/files/{file_id}`
4. `DELETE /portfolio/files/{file_id}`
- Auth: yes
- Optional query for admin override: `user_id` on upload/list
- File rules:
- allowed MIME: PDF, DOC, DOCX
- max size: 10 MB

### 8.5 Public endpoint (`/public`)

1. `GET /public/{username}`
- Auth: no
- Rate limit: yes (`limit_public`)
- Returns: `PublicProfileResponse`
- Data: `name`, `username`, `projects`, `skills`, `experiences`
- Cached by key: `public_profile:{username}`

---

## 9) Migration history (DB evolution)

Order from oldest to newest:
1. `156fb85f5c2d` create `users`
2. `439368655346` make `users.created_by` nullable
3. `4075375ad61c` add `users.role`
4. `9d1f3c7b2a10` create `refresh_tokens`
5. `ba3178f67c22` create portfolio tables (`projects`, `skills`, `experiences`, `resume_files`)
6. `c2f9e5f4b1d0` add `users.username` + backfill + unique index

---

## 10) Environment variables used

Required/used keys:
- `APP_ENV`
- `DATABASE_URL`
- `PUBLIC_BASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM` (default `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `REDIS_URL`
- `PUBLIC_PROFILE_CACHE_TTL_SECONDS`
- `RATE_LIMIT_LOGIN_REQUESTS`
- `RATE_LIMIT_LOGIN_WINDOW_SECONDS`
- `RATE_LIMIT_PUBLIC_REQUESTS`
- `RATE_LIMIT_PUBLIC_WINDOW_SECONDS`

---

## 11) Important implementation notes

- `PUBLIC_PROFILE_CACHE_TTL_SECONDS` controls public profile cache duration (default 300 sec).
- Redis is optional at runtime; app degrades to in-memory cache/rate-limit storage.
- `REFREH_TOKEN_EXPIRE_DAYS` typo key exists as backward fallback in code.
- Root endpoint `/` currently does not return JSON body (only prints to stdout).
- Resume deletion removes DB logical record (`is_deleted=True`) and also deletes disk file if present.

---

## 12) Quick operational flow for AI tools

If an AI tool needs to act on this project safely:
1. Load config keys from `.env`.
2. Ensure DB and Redis reachability.
3. Run migrations to latest revision.
4. Start API server.
5. Use `/auth/register` then `/auth/login` to obtain access token.
6. Call protected endpoints with bearer token.
7. For admin operations, use an admin-role account.
8. For public reads, use `/public/{username}` and expect cache + rate-limit behavior.

---

## 13) Import and dependency map (who imports what)

Entry and routers:
- `portfolio_api/main.py` imports routers from `app.routers`.
- `app/routers/auth.py` imports:
- DB dependency: `app.db.deps.get_db`
- schemas: `app.schemas.auth`
- services: `app.services.auth_service`
- auth dependency: `app.core.deps.get_current_user`
- limiter: `app.core.rate_limit.limit_login`
- user model typing: `app.models.users.User`
- `app/routers/users.py` imports:
- dependencies: `get_db`, `get_current_user`, `require_admin`
- schemas: `app.schemas.user`
- services: `app.services.user_service`
- models: `User`, `UserRole`
- `app/routers/portfolio.py` imports:
- dependencies: `get_db`, `get_current_user`
- schemas: `app.schemas.portfolio`
- services: `app.services.portfolio_service`
- model typing: `app.models.users.User`
- `app/routers/public.py` imports:
- dependency: `get_db`
- limiter: `limit_public`
- schema: `app.schemas.public.PublicProfileResponse`
- service: `app.services.public_service.get_public_profile`

Service to model usage:
- `app/services/auth_service.py` uses models: `User`, `RefreshToken`.
- `app/services/user_service.py` uses model: `User`.
- `app/services/portfolio_service.py` uses models: `Project`, `Skill`, `Experience`, `ResumeFile`, `User`.
- `app/services/public_service.py` uses models: `User`, `Project`, `Skill`, `Experience`.

DB model registration:
- `app/db/models.py` imports all model modules so Alembic can discover metadata:
- `User`, `RefreshToken`, `Project`, `Skill`, `Experience`, `ResumeFile`

---

## 14) SQLAlchemy query patterns and special cases

### 14.1 Common query style in this codebase
- Query builder pattern:
- `db.query(Model).filter(...).first()`
- Pagination pattern:
- `total = query.count()`
- `items = query.order_by(...).offset(offset).limit(limit).all()`
- Mutation pattern:
- set attributes
- `db.commit()`
- optional `db.refresh(instance)`

### 14.2 Auth queries (`app/services/auth_service.py`)

Email lookup:
```python
user = db.query(User).filter(User.email_id == data.email_id).first()
```

Refresh token validation:
```python
stored_token = db.query(RefreshToken).filter(
    RefreshToken.user_id == user_id,
    RefreshToken.jti == jti
).first()
```

Special cases:
- Rejects unknown refresh token row.
- Rejects revoked rows (`revoked_at is not None`).
- Rejects expired rows (`expires_at < datetime.utcnow()`).
- Rejects token hash mismatch (`token_hash != hash_token(refresh_token)`).
- Refresh rotation writes a new row and revokes old row in one commit.

### 14.3 Current user auth query (`app/core/deps.py`)

```python
user = db.query(User).filter(
    User.id == user_id,
    User.is_deleted == False
).first()
```

Special cases:
- Access token must contain `type="access"`.
- Missing user or disabled user returns 401/403 before route logic runs.

### 14.4 User admin queries (`app/services/user_service.py`)

Dynamic filter composition:
```python
query = db.query(User)
if not include_deleted:
    query = query.filter(User.is_deleted == False)
if role:
    query = query.filter(User.role == role)
if is_active is not None:
    query = query.filter(User.is_active == is_active)
if search:
    query = query.filter(
        (User.name.ilike(search_term)) |
        (User.username.ilike(search_term)) |
        (User.email_id.ilike(search_term))
    )
```

Special cases:
- Admin cannot disable own account.
- Username can be auto-generated or provided; provided value is normalized and checked for uniqueness.
- Password validation is enforced on admin user creation and change-password.

### 14.5 Portfolio queries (`app/services/portfolio_service.py`)

Ownership check helper:
```python
record = db.query(model).filter(model.id == record_id, model.is_deleted == False).first()
```

Project listing with search:
```python
query = db.query(Project).filter(Project.user_id == owner_id, Project.is_deleted == False)
if search:
    query = query.filter((Project.title.ilike(term)) | (Project.description.ilike(term)))
```

Special cases:
- Non-admin cannot query/mutate another user's records.
- Delete operations are soft delete (`is_deleted=True`) for DB rows.
- Resume file delete also tries physical disk delete:
- `Path(record.storage_path).unlink()` if exists.
- Every create/update/delete calls cache invalidation for that user's public profile.

### 14.6 Public profile query (`app/services/public_service.py`)

User lookup:
```python
user = db.query(User).filter(
    User.username == username,
    User.is_active == True,
    User.is_deleted == False,
).first()
```

Ordered projections:
- Projects: featured first, newest id first.
- Skills: alphabetical by name.
- Experiences: latest `start_date` first.

Special cases:
- Cached JSON short-circuits DB queries.
- Only active and non-deleted records are published.

---

## 15) Sync vs Async behavior (very important)

Current state:
- All route handlers are synchronous (`def`, not `async def`).
- All DB operations use synchronous SQLAlchemy session (`Session`).
- Redis access is synchronous.
- File I/O for uploads/deletes is synchronous.

Implication:
- FastAPI runs these sync handlers in its threadpool.
- This is valid, but each request does blocking work.
- Heavy DB/file workloads can reduce throughput compared to a full async stack.

Where sync is used:
- Routers: `app/routers/*.py` all `def`.
- Services: pure synchronous functions.
- DB engine/session: `create_engine` + `sessionmaker` sync API.

If migrating to async later:
- Use `create_async_engine` and `AsyncSession`.
- Convert handlers to `async def`.
- Replace blocking file/network calls with async-compatible operations.

---

## 16) Sample code snippets (real usage style)

### 16.1 Login then call protected route
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email_id":"user@example.com","password":"Admin@123"}'
```

```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 16.2 Admin create a user
```bash
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Jane",
    "username":"jane_dev",
    "email_id":"jane@example.com",
    "password":"Strong@123",
    "role":"user",
    "is_verify":true
  }'
```

### 16.3 Create project for current user
```bash
curl -X POST http://localhost:8000/portfolio/projects \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Portfolio API",
    "description":"FastAPI backend",
    "repo_url":"https://github.com/example/repo",
    "live_url":null,
    "is_featured":true
  }'
```

### 16.4 Upload resume file
```bash
curl -X POST "http://localhost:8000/portfolio/files/upload" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@/absolute/path/resume.pdf"
```

### 16.5 Public profile fetch (cached path)
```bash
curl http://localhost:8000/public/<username>
```

Cache behavior:
- First request: DB fetch + cache write.
- Next requests within `PUBLIC_PROFILE_CACHE_TTL_SECONDS`: cache hit.
