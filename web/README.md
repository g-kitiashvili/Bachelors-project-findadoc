# findadoc-web

SvelteKit 2 (with Svelte 5) + TypeScript frontend for Find-a-Doc.

## Prerequisites

- Node.js 20+
- The backend API running on `http://localhost:8080` (or set `API_URL`)

## Run

```bash
npm install
npm run dev
```

Open http://localhost:3000 to browse doctors and clinics served from the API.

## Build for production

```bash
npm run build
node build   # or: npm start
```

The production server runs on port 3000 by default. Configure via env:

| Variable | Default |
|---|---|
| `API_URL` | `http://localhost:8080` (server-side fetch target) |
| `PORT` | `3000` |
| `HOST` | `0.0.0.0` |

## Type-check

```bash
npm run check
```

## Notes

- `+page.server.ts` runs server-side (SSR), fetches API data, passes it to `+page.svelte`.
- The `adapter-node` build outputs a Node.js server in `build/` that serves the SSR'd app — no Vercel or other hosting service required.
