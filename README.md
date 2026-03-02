# Find-a-Doc

Doctor and clinic search for the Georgian healthcare market.

## Repository layout

```
findadoc/
├── README.md
├── docker-compose.yml          unified stack — `docker compose up`
├── .env.example                copy to .env and customize
├── api/                        Kotlin + Spring Boot backend
├── web/                        SvelteKit + TypeScript frontend
└── pipeline/                   Python data-ingestion pipeline
```

## Prerequisites

- **Docker** (with `docker compose`)
- Optional, for local non-containerized dev:
  - **Java 21** (Temurin recommended)
  - **Node.js 20+**
  - **Python 3.11+**

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

This builds and starts Postgres + api + web + pipeline. The first build takes a few minutes; subsequent runs reuse the cached images.

Open <http://localhost:3000>.

To tear down:

```bash
docker compose down        # stops, preserves Postgres volume
docker compose down -v     # also wipes the Postgres data
```

## Local development without Docker

Run Postgres in Docker and the apps natively for hot-reload:

```bash
docker compose up -d postgres

# backend
cd api && ./gradlew bootRun

# frontend (new terminal)
cd web && npm install && npm run dev

# pipeline (new terminal, optional)
cd pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pipeline run --all
```

## License

Non-commercial. Reference material from third parties retains its original rights.
