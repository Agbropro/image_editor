# Retro Scale frontend

## Run locally

From this directory:

```bash
npm install
npm run dev
```

Start the FastAPI backend on `http://localhost:8000`, then open the URL printed by Vite (usually `http://localhost:5173`).

The development server forwards requests beginning with `/api` to FastAPI. For deployment, copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to the backend's public address.
