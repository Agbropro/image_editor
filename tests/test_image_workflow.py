import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageSequence

from src.application.services.crop import CropService
from src.application.services.image import ImageService
from src.application.services.resize import ResizeService
from src.domain.schemas.crop import CropRequest
from src.domain.schemas.resize import ResizeRequest
from src.infrastructure.file_image import FileImageRepository
from src.infrastructure.pillow_image import PillowImageProcessor


class ImageWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repository = FileImageRepository(Path(self.directory.name))
        self.processor = PillowImageProcessor()
        self.images = ImageService(self.repository, self.processor)

    def test_upload_resize_crop_and_reopen_metadata(self):
        source = BytesIO()
        Image.new("RGB", (10, 8), "red").save(source, format="PNG")
        uploaded = self.images.upload("sample.png", source.getvalue())
        resized = ResizeService(self.repository, self.processor, self.processor).resize(uploaded.image_id, ResizeRequest(width=5))
        cropped = CropService(self.repository, self.processor, self.processor).crop(uploaded.image_id, CropRequest((1, 1), (3, 3)))

        metadata = FileImageRepository(Path(self.directory.name)).load_metadata(uploaded.image_id)
        self.assertEqual((resized.version, resized.width, resized.height), (1, 5, 4))
        self.assertEqual((cropped.version, cropped.width, cropped.height), (2, 2, 2))
        self.assertEqual([item.operation for item in metadata.versions], ["upload", "resize", "crop"])
        with Image.open(self.images.current_path(uploaded.image_id)) as current:
            self.assertEqual(current.size, (2, 2))

    def test_animated_gif_keeps_frames_timing_and_loop(self):
        source = BytesIO()
        first = Image.new("RGB", (6, 4), "red")
        second = Image.new("RGB", (6, 4), "blue")
        first.save(source, format="GIF", save_all=True, append_images=[second], duration=[80, 120], loop=3)
        uploaded = self.images.upload("animation.gif", source.getvalue())
        response = ResizeService(self.repository, self.processor, self.processor).resize(uploaded.image_id, ResizeRequest(width=3))

        self.assertEqual(response.frames, 2)
        with Image.open(self.images.current_path(uploaded.image_id)) as current:
            self.assertEqual(current.size, (3, 2))
            self.assertEqual(current.info["loop"], 3)
            self.assertEqual([frame.info["duration"] for frame in ImageSequence.Iterator(current)], [80, 120])

    def test_invalid_requests_do_not_create_versions(self):
        source = BytesIO()
        Image.new("RGB", (10, 8)).save(source, format="JPEG")
        uploaded = self.images.upload("sample.jpg", source.getvalue())
        resize = ResizeService(self.repository, self.processor, self.processor)
        crop = CropService(self.repository, self.processor, self.processor)

        with self.assertRaises(ValueError):
            resize.resize(uploaded.image_id, ResizeRequest(width=0))
        with self.assertRaises(ValueError):
            crop.crop(uploaded.image_id, CropRequest((4, 4), (2, 6)))
        self.assertEqual(self.images.details(uploaded.image_id).current_version, 0)
        with self.assertRaises(ValueError):
            self.images.upload("bad.png", b"not an image")


if __name__ == "__main__":
    unittest.main()
