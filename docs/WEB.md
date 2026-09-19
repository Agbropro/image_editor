# Retro Scale frontend guide

This document explains where the frontend code lives, how the page moves through its workflow, which backend API each control calls, and where to add your own art or animation.

The frontend is a Vite + React + TypeScript application. It is intentionally a single page: there is currently no React Router and there are no separate frontend URLs for upload, resize, or download.

## 1. Start the website

Start the backend first on port `8000`, then run:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite address, normally `http://localhost:5173`.

During development, [`frontend/vite.config.ts`](../frontend/vite.config.ts) forwards every `/api` request to `http://localhost:8000`. This means the browser talks to the frontend server, and Vite talks to FastAPI.

For deployment, create `frontend/.env`:

```env
VITE_API_BASE_URL=https://your-api-domain.example.com
```

The API helper combines this value with `/api/v1`.

## 2. Frontend file map

| File | Purpose | Edit this when... |
|---|---|---|
| [`frontend/src/App.tsx`](../frontend/src/App.tsx) | Main page layout, form state, button actions, preview cards | You want to add or remove UI controls or change the page flow |
| [`frontend/src/api.ts`](../frontend/src/api.ts) | All calls to FastAPI and API response types | A backend route, request body, or response shape changes |
| [`frontend/src/styles.css`](../frontend/src/styles.css) | Colors, layout, pixel borders, responsive behavior, font styling | You want to change the visual design or add CSS animation |
| [`frontend/src/main.tsx`](../frontend/src/main.tsx) | React entrypoint; attaches `App` to the HTML page | You need global providers or application startup behavior |
| [`frontend/index.html`](../frontend/index.html) | Browser document shell and page title | You want to change the HTML title or add global metadata |
| [`frontend/vite.config.ts`](../frontend/vite.config.ts) | Local dev server and API proxy | The backend address or frontend port changes |
| [`frontend/.env.example`](../frontend/.env.example) | Deployment configuration example | You want to document a new environment variable |

The easiest rule is: edit `App.tsx` for behavior and `styles.css` for appearance. Keep network code in `api.ts` instead of writing `fetch()` calls directly inside visual components.

## 3. Page navigation and workflow

There is no route navigation yet. The page changes by React state:

```text
initial page
  ↓ choose file
uploadImage()
  ↓ image metadata is saved in `image`
original preview appears
  ↓ enter resize values and press RESIZE
resizeImage()
  ↓ resize metadata is saved in `result`
modified preview appears
  ↓ press DOWNLOAD RESULT
browser downloads the current backend version
```

The main state is defined near the top of `App()`:

- `image`: metadata for the uploaded image, including its `image_id`.
- `result`: metadata for the resized version, including its version number.
- `inputMode`: selected aspect-preserving mode: width, height, or scale.
- `value`: the single value used when aspect ratio is maintained.
- `widthValue` and `heightValue`: the two values used when aspect ratio is not maintained.
- `keepRatio`: whether the aspect-ratio checkbox is checked.
- `busy`: disables controls while an API call is running.
- `message` and `error`: user-facing status text.

### Aspect-ratio form rules

When `keepRatio` is true, `App.tsx` renders one resize mode and one value field:

- Width: `{ "width": number, "maintain_aspect_ratio": true }`
- Height: `{ "height": number, "maintain_aspect_ratio": true }`
- Scale: `{ "scale": number, "maintain_aspect_ratio": true }`

When `keepRatio` is false, it renders two fields and sends:

```json
{
  "width": 800,
  "height": 600,
  "maintain_aspect_ratio": false
}
```

The frontend validates values before sending them. The backend performs its own validation as well.

## 4. Backend API map

The API functions are in [`frontend/src/api.ts`](../frontend/src/api.ts). The following controls use them:

| UI control | Frontend function | HTTP request | Backend route |
|---|---|---|---|
| Choose file / `UPLOAD IMAGE` | `uploadImage(file)` | `POST /api/v1/images` with multipart field `file` | [`src/routes/image.py`](../src/routes/image.py), `upload_image()` |
| Original preview | `imageViewUrl(image.image_id)` | `GET /api/v1/images/{image_id}/view` | `view()` in `src/routes/image.py` |
| `RESIZE` button | `resizeImage(image.image_id, values)` | `POST /api/v1/images/{image_id}/resize` with JSON body | [`src/routes/resize.py`](../src/routes/resize.py), `resize_image()` |
| Modified preview | `imageViewUrl(result.image_id, result.version)` | `GET /api/v1/images/{image_id}/view?version={version}` | `view()` in `src/routes/image.py` |
| `DOWNLOAD RESULT` | `imageDownloadUrl(result.image_id)` | `GET /api/v1/images/{image_id}/download` | `download()` in `src/routes/image.py` |

The `version` query string is currently used as a browser cache-buster. The backend route selects the current image version from metadata; if you later want to view an older version, the backend will need an explicit version parameter and the frontend helper will need to match it.

The upload response is stored in `image`. The resize response is stored in `result`. This is why the original preview uses `image.image_id`, while the modified preview only appears after a successful resize.

## 5. Where to put custom assets

Create these folders when you begin adding official artwork:

```text
frontend/src/assets/
├── images/       # logos, decorative pixel art, backgrounds
├── icons/        # small UI icons and button symbols
└── fonts/        # self-hosted .woff2 or .ttf files
```

For an imported asset:

```tsx
import mascotImage from "./assets/images/mascot.png";

<img src={mascotImage} alt="Retro Scale mascot" />
```

Then add the related style in `styles.css`:

```css
.mascot-image {
  width: 96px;
  image-rendering: pixelated;
}
```

For a file that should keep its public URL without importing it, use `frontend/public/`:

```text
frontend/public/assets/background-grid.png
```

Then reference it as:

```tsx
<img src="/assets/background-grid.png" alt="" />
```

Prefer `src/assets/` for normal application artwork because Vite checks and bundles imported files. Use `public/` for files that need a stable direct URL.

### Replacing the temporary font

The current temporary font is loaded at the top of `styles.css` using Google Fonts. To use your own font, put the font file in `frontend/src/assets/fonts/` and replace the import with an `@font-face` rule:

```css
@font-face {
  font-family: "MyRetroFont";
  src: url("./assets/fonts/my-retro-font.woff2") format("woff2");
  font-weight: normal;
  font-style: normal;
}

:root {
  font-family: "MyRetroFont", monospace;
}
```

## 6. Adding animation

Choose the simplest type of animation for the job.

### CSS animation

Use this for blinking text, button movement, scanlines, or decorative effects. Add a `@keyframes` block to `styles.css`, then add its class to the JSX in `App.tsx`:

```css
@keyframes blink {
  50% { opacity: 0.35; }
}

.header-status {
  animation: blink 1.2s steps(2, jump-none) infinite;
}
```

### Animated image asset

For a pixel-art GIF or animated WebP, put it in `src/assets/images/` and import it like any other image. The browser animates it automatically:

```tsx
import loadingSprite from "./assets/images/loading-sprite.gif";

<img src={loadingSprite} alt="Loading" />
```

### Animation controlled by React state

Use this when animation depends on upload or resize status. The existing `busy` state is already available. For example, add a class conditionally:

```tsx
<section className={`control-panel ${busy ? "is-busy" : ""}`}>
```

Then animate `.is-busy` in `styles.css`.

### Important accessibility rule

For motion that is not essential, add a reduced-motion fallback:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 7. Adding a new UI feature

Use this sequence:

1. Add or update a TypeScript type in `api.ts` if the backend response changes.
2. Add a small API function in `api.ts`.
3. Add state with `useState` in `App.tsx` if the feature needs memory.
4. Add an event handler such as `handleUpload` or `handleResize`.
5. Add the JSX control or component.
6. Add visual styling in `styles.css`.
7. Run `npm run build` from `frontend/`.

For a large feature, move it into a new component such as `frontend/src/components/HistoryPanel.tsx`, then import that component into `App.tsx`. The current project is small enough that `App.tsx` is intentionally kept as the main readable starting point.

## 8. Useful commands

```bash
cd frontend
npm run dev       # local development with hot reload
npm run build     # TypeScript check and production build
npm run preview   # preview the production build locally
```

The generated `frontend/dist/` folder is build output and is ignored by Git. Do not edit it directly; edit `src/` and build again.
