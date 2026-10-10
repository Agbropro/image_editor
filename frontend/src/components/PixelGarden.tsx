import { pixelGarden, sparkleIcon } from "../assets";

// Decorative artwork stays separate from upload and resize behavior.
export default function PixelGarden() {
  return (
    <div className="pixel-garden" aria-hidden="true">
      <img className="pixel-garden-scene" src={pixelGarden} alt="" />
      <img className="garden-sparkle garden-sparkle-left" src={sparkleIcon} alt="" />
      <img className="garden-sparkle garden-sparkle-right" src={sparkleIcon} alt="" />
    </div>
  );
}
