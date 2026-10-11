from io import BytesIO

from PIL import Image, ImageSequence, UnidentifiedImageError

from src.application.ports.crop import CropProcessor
from src.application.ports.image import ImageInspector
from src.application.ports.resize import ResizeProcessor
from src.domain.schemas.crop import CropRequest
from src.domain.schemas.image import ImageInfo


class PillowImageProcessor(ImageInspector, ResizeProcessor, CropProcessor):
    def inspect(self, content: bytes) -> ImageInfo:
        try:
            with Image.open(BytesIO(content)) as image:
                image.load()
                return ImageInfo(image.format, image.width, image.height, getattr(image, "n_frames", 1))
        except (UnidentifiedImageError, OSError) as error:
            raise ValueError("Invalid image file") from error

    def resize(self, content: bytes, width: int, height: int) -> tuple[bytes, ImageInfo]:
        """Use nearest-neighbor for GIF frames and Lanczos for still images."""
        with Image.open(BytesIO(content)) as image:
            if image.format == "GIF":
                # Nearest-neighbor keeps pixel art edges crisp when GIF frames are scaled.
                return self._animated(image, lambda frame: frame.resize((width, height), Image.Resampling.NEAREST))
            edited = image.resize((width, height), Image.Resampling.LANCZOS)
            return self._encode(edited, image.format)

    def crop(self, content: bytes, request: CropRequest) -> tuple[bytes, ImageInfo]:
        left, top = request.top_left_point
        right, bottom = request.bottom_right_point
        with Image.open(BytesIO(content)) as image:
            box = (left, top, right, bottom)
            if image.format == "GIF":
                return self._animated(image, lambda frame: frame.crop(box))
            return self._encode(image.crop(box), image.format)

    def _animated(self, image: Image.Image, edit) -> tuple[bytes, ImageInfo]:
        """Apply an edit to every GIF frame while keeping playback timing and repeat count."""
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(image):
            frames.append(edit(frame.convert("RGBA")))
            # Duration is the delay before the next frame; use 100 ms if the file omits it.
            durations.append(frame.info.get("duration", image.info.get("duration", 100)))
        output = BytesIO()
        # loop=0 means repeat forever. Disposal tells the player what to do with the
        # previous frame before showing the next; 2 clears the previous frame to the
        # background, preventing leftover pixels when frames change size or position.
        # Pillow also accepts one disposal value per frame if that is needed later.
        frames[0].save(output, format="GIF", save_all=True, append_images=frames[1:], duration=durations, loop=image.info.get("loop", 0), disposal=2)
        content = output.getvalue()
        return content, self.inspect(content)

    def _encode(self, image: Image.Image, image_format: str) -> tuple[bytes, ImageInfo]:
        # JPEG cannot store alpha transparency, so convert transparent image modes to RGB.
        if image_format == "JPEG" and image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        output = BytesIO()
        image.save(output, format=image_format)
        content = output.getvalue()
        return content, self.inspect(content)
