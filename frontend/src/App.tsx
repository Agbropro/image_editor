import { ChangeEvent, FormEvent, useState } from "react";
import { imageDownloadUrl, imageViewUrl, ImageInfo, resizeImage, ResizeResult, uploadImage } from "./api";
import { handheldIcon } from "./assets";
import PixelGarden from "./components/PixelGarden";

type InputMode = "width" | "height" | "scale";

function App() {
  const [image, setImage] = useState<ImageInfo | null>(null);
  const [result, setResult] = useState<ResizeResult | null>(null);
  const [inputMode, setInputMode] = useState<InputMode>("width");
  const [value, setValue] = useState("");
  const [widthValue, setWidthValue] = useState("");
  const [heightValue, setHeightValue] = useState("");
  const [keepRatio, setKeepRatio] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Choose an image to begin.");
  const [error, setError] = useState("");

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setBusy(true);
    setError("");
    setMessage("Uploading image...");
    try {
      const uploadedImage = await uploadImage(file);
      setImage(uploadedImage);
      setResult(null);
      setMessage("Image ready. Choose one resize value.");
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed.");
      setMessage("Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleResize(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!image) {
      setError("Upload an image first.");
      return;
    }

    const numberValue = Number(value);
    const numberWidth = Number(widthValue);
    const numberHeight = Number(heightValue);
    if (keepRatio && (!Number.isFinite(numberValue) || numberValue <= 0)) {
      setError("Enter a number greater than zero.");
      return;
    }
    if (!keepRatio && (!Number.isFinite(numberWidth) || numberWidth <= 0 || !Number.isFinite(numberHeight) || numberHeight <= 0)) {
      setError("Enter both width and height values greater than zero.");
      return;
    }

    setBusy(true);
    setError("");
    setMessage("Resizing image...");
    try {
      const resizeValues = {
        ...(!keepRatio ? { width: numberWidth, height: numberHeight } : {}),
        ...(keepRatio && inputMode === "width" ? { width: numberValue } : {}),
        ...(keepRatio && inputMode === "height" ? { height: numberValue } : {}),
        ...(keepRatio && inputMode === "scale" ? { scale: numberValue } : {}),
        maintain_aspect_ratio: keepRatio,
      };
      const resizedImage = await resizeImage(image.image_id, resizeValues);
      setResult(resizedImage);
      setMessage("Resize complete. Your modified image is ready.");
    } catch (resizeError) {
      setError(resizeError instanceof Error ? resizeError.message : "Resize failed.");
      setMessage("Resize failed.");
    } finally {
      setBusy(false);
    }
  }

  const modifiedImageUrl = result ? imageViewUrl(result.image_id, result.version) : "";

  return (
    <main className="page-shell">
      <header className="site-header">
        <div className="brand-mark" aria-hidden="true"><img src={handheldIcon} alt="" /></div>
        <div>
          <p className="eyebrow">GAMEBOY IMAGE LAB</p>
          <h1>RETRO SCALE</h1>
        </div>
        <span className="header-status">● ONLINE</span>
      </header>

      <section className="control-panel pixel-border">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">IMAGE RESIZER</p>
            <h2>MAKE IT FIT</h2>
          </div>
          <span className="panel-number">01</span>
        </div>

        <label className="upload-button">
          <span>{busy ? "WORKING..." : "UPLOAD IMAGE"}</span>
          <input type="file" accept="image/png,image/jpeg,image/gif,image/webp" onChange={handleUpload} disabled={busy} />
        </label>

        <form onSubmit={handleResize}>
          <label className="checkbox-row">
            <input type="checkbox" checked={keepRatio} onChange={(event) => setKeepRatio(event.target.checked)} />
            <span>MAINTAIN ASPECT RATIO</span>
          </label>

          <div className={`resize-inputs ${keepRatio ? "single-input" : "free-inputs"}`}>
            {keepRatio ? <>
              <label className="field-label">
                RESIZE BY
                <select value={inputMode} onChange={(event) => setInputMode(event.target.value as InputMode)}>
                  <option value="width">WIDTH (PX)</option>
                  <option value="height">HEIGHT (PX)</option>
                  <option value="scale">SCALE (TIMES)</option>
                </select>
              </label>
              <label className="field-label">
                VALUE
                <input type="number" min="0.01" step="any" value={value} onChange={(event) => setValue(event.target.value)} placeholder=" e.g. 500" />
              </label>
            </> : <>
              <label className="field-label">
                WIDTH (PX)
                <input type="number" min="1" step="1" value={widthValue} onChange={(event) => setWidthValue(event.target.value)} placeholder=" e.g. 800" />
              </label>
              <label className="field-label">
                HEIGHT (PX)
                <input type="number" min="1" step="1" value={heightValue} onChange={(event) => setHeightValue(event.target.value)} placeholder=" e.g. 600" />
              </label>
            </>}
            <button className="button-primary" type="submit" disabled={busy || !image}>RESIZE</button>
          </div>
        </form>

        <p className="status-message">{message}</p>
        {error && <p className="error-message">ERROR: {error}</p>}
      </section>

      <section className="preview-grid">
        <PreviewCard title="ORIGINAL" imageUrl={image ? imageViewUrl(image.image_id) : ""} details={image ? `${image.width} × ${image.height} / ${image.frames} FRAME${image.frames === 1 ? "" : "S"}` : "WAITING FOR IMAGE"} />
        <div className="arrow-divider" aria-hidden="true">→</div>
        <PreviewCard title="MODIFIED" imageUrl={modifiedImageUrl} details={result ? `${result.width} × ${result.height} / VERSION ${result.version}` : "RESIZE TO SEE RESULT"} />
      </section>

      <a className={`download-button ${result ? "is-ready" : ""}`} href={result ? imageDownloadUrl(result.image_id) : undefined} aria-disabled={!result} onClick={(event) => { if (!result) event.preventDefault(); }}>
        DOWNLOAD RESULT
      </a>

      <PixelGarden />
      <footer>RETRO SCALE // IMAGE EDITOR // BUILD 001</footer>
    </main>
  );
}

function PreviewCard({ title, imageUrl, details }: { title: string; imageUrl: string; details: string }) {
  return (
    <article className="preview-card pixel-border">
      <div className="preview-title">{title}</div>
      <div className="preview-window">
        {imageUrl ? <img src={imageUrl} alt={`${title.toLowerCase()} preview`} /> : <img className="empty-preview-art" src={handheldIcon} alt="No image yet" />}
      </div>
      <p className="preview-details">{details}</p>
    </article>
  );
}

export default App;
