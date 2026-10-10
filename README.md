# Retro Scale

Retro Scale is a browser image resizer backed by a FastAPI API. The frontend is React, TypeScript, and Vite; image processing uses Pillow. The API accepts still images and animated GIFs and stores uploaded files and derived versions locally.

## Run locally

Use Python 3.10+ and Node.js with npm.

Install backend dependencies and start the API from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.app:app --reload
```

In another terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite forwards `/api` requests to the API at `http://localhost:8000`. For a frontend served separately, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL` to the API origin.

## API

All routes use the `/api/v1` prefix. FastAPI's interactive API reference is at `http://localhost:8000/docs`.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/images` | Upload an image as multipart field `file`; returns its ID and dimensions. |
| `GET` | `/images/{image_id}/details` | Read image version metadata. |
| `GET` | `/images/{image_id}/view` | View the current image version inline. |
| `GET` | `/images/{image_id}/download` | Download the current image version. |
| `POST` | `/images/{image_id}/resize` | Resize the current version; accepts `width`, `height`, `scale`, and `maintain_aspect_ratio`. |
| `GET` | `/health` | API health status. |
| `GET` | `/versions` | API version and description from `config/config.yaml`. |

The resize request is JSON. With aspect ratio enabled, provide one of `width`, `height`, or `scale`; with it disabled, provide both `width` and `height`. A successful resize is saved as a new version and becomes current. GIF frames are resized with their timing and loop metadata.

## Storage and code layout

Uploads, `metadata.json`, and generated versions are stored under `data/images/{image_id}/`. This directory is generated at runtime and is ignored by Git.

```text
src/app.py                 FastAPI application and route registration
src/routes/                HTTP endpoints
src/services/              Image storage and Pillow operations
src/domain/schemas/        Request and response models
frontend/src/              React application and API client
config/config.yaml         API version metadata
```

Crop service and schemas exist in `src/services/crop.py` and `src/domain/schemas/crop.py`, but crop is not currently registered as an API route.
