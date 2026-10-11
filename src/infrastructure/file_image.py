import json
import re
from dataclasses import asdict
from pathlib import Path

from src.application.ports.image import ImageRepository
from src.domain.schemas.image import ImageInfo, ImageMetadata, ImageVersion


class FileImageRepository(ImageRepository):
    def __init__(self, storage_path: Path | str = "data/images") -> None:
        self.storage_path = Path(storage_path)

    def _directory(self, image_id: str) -> Path:
        if re.fullmatch(r"[A-Za-z0-9_-]+", image_id) is None:
            raise FileNotFoundError(f"Image not found: {image_id}")
        return self.storage_path / image_id

    def _metadata_path(self, image_id: str) -> Path:
        return self._directory(image_id) / "metadata.json"

    def save_original(self, image_id: str, filename: str, content: bytes, info: ImageInfo) -> ImageMetadata:
        """Save the upload as version zero and create its metadata file."""
        extension = {"JPEG": ".jpg", "PNG": ".png", "GIF": ".gif", "WEBP": ".webp", "BMP": ".bmp", "TIFF": ".tif"}.get(info.format)
        if extension is None:
            raise ValueError(f"Unsupported image format: {info.format}")
        directory = self._directory(image_id)
        directory.mkdir(parents=True, exist_ok=False)
        path = directory / f"original{extension}"
        path.write_bytes(content)
        metadata = ImageMetadata(image_id, 0, [ImageVersion(0, path.name, "upload", info.format, info.width, info.height, info.frames)])
        self._save_metadata(metadata)
        return metadata

    def load_metadata(self, image_id: str) -> ImageMetadata:
        """Rebuild nested dataclasses from the stored JSON metadata."""
        with self._metadata_path(image_id).open(encoding="utf-8") as file:
            data = json.load(file)
        return ImageMetadata(data["image_id"], data["current_version"], [ImageVersion(**version) for version in data["versions"]])

    def _save_metadata(self, metadata: ImageMetadata) -> None:
        self._metadata_path(metadata.image_id).write_text(json.dumps(asdict(metadata), indent=4), encoding="utf-8")

    def current_path(self, image_id: str) -> Path:
        """Find the file selected by current_version in metadata.json."""
        metadata = self.load_metadata(image_id)
        version = next(version for version in metadata.versions if version.version == metadata.current_version)
        path = self._directory(image_id) / version.file
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {image_id}")
        return path

    def current_content(self, image_id: str) -> bytes:
        return self.current_path(image_id).read_bytes()

    def save_version(self, image_id: str, content: bytes, info: ImageInfo, operation: str) -> int:
        """Write v001, v002, ... and record the new current version."""
        metadata = self.load_metadata(image_id)
        # The highest saved version is used so an existing file is never overwritten.
        version = max(item.version for item in metadata.versions) + 1
        extension = self.current_path(image_id).suffix
        filename = f"v{version:03d}{extension}"
        (self._directory(image_id) / filename).write_bytes(content)
        # Keep the version record in sync with the file that was just written.
        metadata.versions.append(ImageVersion(version, filename, operation, info.format, info.width, info.height, info.frames))
        metadata.current_version = version
        self._save_metadata(metadata)
        return version

    def set_current_version(self, image_id: str, version: int) -> ImageMetadata:
        metadata = self.load_metadata(image_id)

        saved_version = next(
            (item for item in metadata.versions if item.version == version),
            None,
        )
        if saved_version is None:
            raise FileNotFoundError(f"Version {version} not found for image: {image_id}")

        if not (self._directory(image_id) / saved_version.file).is_file():
            raise FileNotFoundError(f"File for version {version} not found: {image_id}")

        metadata.current_version = version
        self._save_metadata(metadata)
        return metadata
