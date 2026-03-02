# findadoc-api

Kotlin + Spring Boot 3 backend for Find-a-Doc.

## Prerequisites

- Java 21 (Temurin recommended)
- A running PostgreSQL on `localhost:5432` with database `findadoc` (or set the env vars below)
  - Easy: `docker compose up -d postgres` from the repo root.

## Run

```bash
./gradlew bootRun
```

The app listens on `http://localhost:8080`. Sanity checks:

- `curl http://localhost:8080/actuator/health` → `{"status":"UP"}`
- `curl http://localhost:8080/api/v1/doctors/test-doctor` → `{"slug":"test-doctor","fullName":"Test Doctor"}`

## Build & test

```bash
./gradlew build           # compile + run tests + assemble jar
./gradlew compileKotlin   # compile only (no tests)
./gradlew test            # run tests
```

## Configuration

Environment variables (see `application.yml` for defaults):

| Variable | Default |
|---|---|
| `DATABASE_URL` | `jdbc:postgresql://localhost:5432/findadoc` |
| `DATABASE_USERNAME` | `findadoc` |
| `DATABASE_PASSWORD` | `findadoc` |

## Database migrations

Flyway runs migrations from `src/main/resources/db/migration/` on startup. Add new migrations as `VNNNN__description.sql` — never modify a migration that has already been deployed.
