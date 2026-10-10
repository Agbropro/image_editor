# Retro Scale artwork and theme guide

## Pending Game Boy date revision

`frontend/src/assets/images/gameboy-date-draft.png` contains the generated couple: the blonde girl in her red dress and a man wearing a cream canvas jacket, maroon shirt, and blue jeans, each holding a handheld console, with a heart bubble above them. It was made using the built-in image-generation tool from the original garden reference.

This is a draft, not imported by the UI: its checkerboard background is baked into the RGB pixels, not actual transparency. A follow-up request to replace the checkerboard with flat `#80b77d` failed because the image-generation usage limit was reached. The existing garden remains active. Once corrected, update the `pixelGarden` export in `frontend/src/assets/index.ts` to the final asset path.

Revision prompt: preserve the wide pixel garden; add a man in a cream canvas jacket, maroon shirt and blue jeans beside the blonde girl in a red dress; both play handheld consoles on a date; add a floating cream bubble with a red heart. Request a transparent backdrop to reveal the website sage green. Correction prompt: preserve the couple and garden, replace all checkerboard pixels with perfectly flat RGB(128, 183, 125), `#80b77d`, without texture or gradients.

Start with `frontend/src/assets/index.ts` to replace artwork, and the `:root` block in `frontend/src/styles.css` to change UI colors and fonts. All artwork created for this update lives inside `frontend/src/assets/` and is imported from there. No generated image depends on a file outside the repository.

## Asset inventory

| Asset path (relative to repository) | Named import | Where it appears | Where to change size/placement |
| --- | --- | --- | --- |
| `frontend/src/assets/images/pixel-garden.png` | `pixelGarden` | `PixelGarden` below Download Result: blonde girl in a red dress, handheld console, flowers, grass, mushrooms, butterfly | `.pixel-garden` and `.pixel-garden-scene` in `styles.css` |
| `frontend/src/assets/icons/handheld.svg` | `handheldIcon` | Header brand and empty preview cards in `App.tsx` | `.brand-mark img` and `.preview-window .empty-preview-art` |
| `frontend/src/assets/icons/sparkle.svg` | `sparkleIcon` | Two floating decorations in `PixelGarden` | `.garden-sparkle`, `.garden-sparkle-left`, `.garden-sparkle-right` |

The garden is one combined image (2172 × 724 pixels), including the girl. To replace only the girl, edit/regenerate that scene or introduce a separate transparent character asset. The garden has an opaque green background; changing the site's green does not recolor it. The SVG icons are separate editable files composed of simple pixel-aligned paths. Change their `fill` colors in the SVG source; CSS theme variables do not recolor images loaded with `<img>`.

## Components and edit locations

| Component or UI section | File | Responsibility |
| --- | --- | --- |
| `App` | `frontend/src/App.tsx` | Page order, header, upload, aspect-ratio controls, resize, download, status and footer |
| `PreviewCard` | Bottom of `frontend/src/App.tsx` | Original/modified preview, empty handheld illustration, dimensions and version text |
| `PixelGarden` | `frontend/src/components/PixelGarden.tsx` | Decorative garden scene and floating sparkles; makes no API calls |
| Asset exports | `frontend/src/assets/index.ts` | Central list of asset names and file imports |
| Theme/layout | `frontend/src/styles.css` | Fonts, colors, borders, spacing, responsive layout and animation |
| Browser title | `frontend/index.html` | Tab title and theme-color metadata |
| API helpers | `frontend/src/api.ts` | Backend requests; see `docs/WEB.md` for button-to-endpoint mapping |

The `PixelGarden` JSX line in `App.tsx` controls its place on the page. Move that line to move the whole decoration. Its artwork cannot intercept clicks (`pointer-events: none`) and is hidden from screen readers (`aria-hidden="true"`) because it is decorative. Keep meaningful instructions in normal HTML text rather than putting them inside artwork.

## Replace or add artwork

To replace an existing asset, put your new PNG/WebP/SVG in the matching assets subfolder and change its export path in `assets/index.ts`. Keep the export name the same and every consuming component updates automatically.

To add a new asset, for example `frontend/src/assets/images/cloud.png`:

```ts
// frontend/src/assets/index.ts
export { default as cloudImage } from "./images/cloud.png";
```

```tsx
// In frontend/src/components/PixelGarden.tsx
import { cloudImage } from "../assets";

// Add inside the component's returned JSX:
<img className="garden-cloud" src={cloudImage} alt="" />
```

```css
/* frontend/src/styles.css */
.garden-cloud {
  position: absolute;
  left: 20%;
  top: 8%;
  width: 64px;
  image-rendering: pixelated;
}
```

These cloud snippets are examples, not installed assets. From `App.tsx` the import path is `./assets`; from a file under `components/` it is `../assets`. The difference is simply directory depth. Importing assets lets the build check paths and give files cache-safe output names. Do not edit generated files in `frontend/dist/`.

## Fonts

Both existing fonts are loaded by the Google Fonts `@import` at the top of `styles.css`; no font binaries were added in this update. They require network access, with a local monospace fallback.

| Theme variable | Current font | Used for |
| --- | --- | --- |
| `--font-body` | `"VT323", monospace` | Form fields, status text, preview details |
| `--font-pixel` | `"Press Start 2P", monospace` | Headings, buttons, brand, labels and footer |

To self-host a font, create `frontend/src/assets/fonts/`, put a properly licensed `.woff2` file there, then add this to `styles.css` after any remaining `@import` statements:

```css
@font-face {
  font-family: "My Pixel Font";
  src: url("./assets/fonts/my-pixel-font.woff2") format("woff2");
  font-display: swap;
}
```

Change `--font-pixel` to `"My Pixel Font", monospace` in `:root`. Remove the Google Fonts import only when neither Google font is needed. Fonts are consumed through CSS `url(...)`, unlike artwork's TypeScript imports.

## Colors

All UI theme variables live at the top of `frontend/src/styles.css`.

| Variable | Value | Purpose |
| --- | --- | --- |
| `--color-sage` | `#80b77d` | Page background and input fill |
| `--color-forest` | `#285238` | Primary buttons, borders, panel shadows |
| `--color-ink` | `#2b1303` | Main text and dark outlines |
| `--color-cream` | `#f4e8c1` | Panel surfaces and button text |
| `--color-brown` | `#64370a` | Download button and secondary details |
| `--color-checker` | `#a6ce91` | Lighter preview checkerboard squares |
| `--color-error` | `#8d1d12` | Error text |

The illustrations add blonde gold and brick-red accents. Their colors are embedded in the PNG/SVG files, independent of these variables. Update `theme-color` in `frontend/index.html` separately if you change the browser chrome color.

## Animation and responsive behavior

The garden itself is a still image. The two sparkles move vertically by eight CSS pixels with `garden-float` in `styles.css`; `steps(4, end)` gives discrete retro movement. Change the `4s` duration, keyframe distance, or `.garden-sparkle-right` delay to adjust it. Delete the `animation` property to stop it. The `prefers-reduced-motion` rule already disables this decorative motion for users requesting less motion.

For animated sprites, import a GIF/WebP via `assets/index.ts` and render an `<img>` the same way. The browser plays the file automatically; CSS reduced-motion rules do not pause animated image files, so provide a static alternative for reduced-motion users when adding one.

The garden scales proportionally to the page width without cropping. The UI switches to its mobile layout at 700px. Small icons use `image-rendering: pixelated` to retain crisp edges. Keep decorations away from form text and preserve visible labels when replacing button art.

## Creation notes and verification

The garden was generated with the built-in image generation tool. The handheld and sparkle SVG icons were authored as simple code-native UI graphics. The generation prompt was:

> Create one production website asset: a wide 3:1 pixel-art garden vignette for Retro Scale, a retro handheld game inspired image editing website. A cheerful blonde girl wearing a modest red dress and brown boots stands on the RIGHT third, holding a tiny cream handheld game console. Small cream flowers, grass tufts, two mushrooms and a butterfly decorate a low grassy platform along the bottom; upper left mostly empty. Authentic chunky low-resolution 16-bit sprite art, crisp square pixels, limited palette: sage #80b77d, forest #285238, brown #64370a, dark brown #2b1303, cream #f4e8c1, golden blonde and muted brick red. Flat solid sage #80b77d background (not transparency), no gradients, no text, no watermark. Entire composition within frame. This is a decorative footer landscape, not a screenshot or UI mockup.

The generated background has some texture, so it may not blend exactly with the flat CSS background. It is presented as a separate garden vignette.

After editing, run `npm run build` inside `frontend/` to catch missing imports and TypeScript errors. Use `npm run dev` to check desktop/mobile placement and upload/resize behavior in your browser.
