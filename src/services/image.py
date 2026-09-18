from pydantic import BaseModel
import json
import random
import time
from pathlib import Path
from PIL import Image
from src.domain.schemas.image import ImageMetadata, ImageVersion, ImageInfo

class ImageService:

    def __init__(self, storage_path: str = "data/images")->str:
        """Initialize the image service."""
        self.storage_path = Path(storage_path)
        self.log_block = "Image-Service"
    def generate_image_id(self) -> str:
        """Create an image ID for the uploaded file."""
        timestamp = int(time.time() * 1000)
        rand_num = random.randint(0, 9999)
        image_id = f"{timestamp}_{rand_num}"
        print(f"[{image_id}] [{self.log_block}] Generated ID : {image_id}")
        return image_id

    def create_image_dir(self, image_id: str) -> Path:
        """Create a directory to save the uploaded file."""
        image_dir = self.storage_path / image_id
        image_dir.mkdir(parents=True,exist_ok=True)
        return image_dir

    def save_original(
        self,
        image_id: str,
        filename: str,
        content: bytes
    ) -> Path:
        """Save the uploaded file to the directory."""
        image_dir = self.create_image_dir(image_id=image_id)
        extension = Path(filename).suffix
        output_path = image_dir / f"original{extension}"
        output_path.write_bytes(content)
        print(f"[{image_id}] [{self.log_block}] image {image_id} saved to {output_path}")
        return output_path

    def get_image_dir(self, image_id: str) -> Path:
        """Get the path to the image directory."""
        image_dir = self.storage_path / image_id
        print(f"[{image_id}] [{self.log_block}] Image dir of image {image_id} : {image_dir}")
        return image_dir

    def create_metadata(
        self,
        image_id: str,
        inspect_result: ImageInfo,
        saved_path: Path,
    ) -> ImageMetadata:
        """Create metadata for the uploaded image."""
        metadata = ImageMetadata(
            image_id=image_id,
            current_version=0,
            versions=[
                ImageVersion(
                    version=0,
                    file=saved_path.name,
                    operation="upload",
                    format=inspect_result.format,
                    width=inspect_result.width,
                    height=inspect_result.height,
                    frames=inspect_result.frames,
                )
            ],
        )

        self.save_metadata(
            image_id=image_id,
            metadata=metadata,
        )
        print(f"[{image_id}] [{self.log_block}] Metadata has been created for image {image_id} | saved in {image_id}")
        return metadata

    def load_metadata(self, image_id: str) -> ImageMetadata:
        """Load metadata for the uploaded image."""
        metadata_path = self.get_image_dir(image_id) / "metadata.json"

        if not metadata_path.exists():
            print(f"[{image_id}] [{self.log_block}] Metadata not found for image {image_id}")
            raise FileNotFoundError(
                f"Metadata not found for image: {image_id}"
            )

        print(f"[{image_id}] [{self.log_block}] Opening Metadata for image {image_id}")
        with metadata_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return ImageMetadata(**data)

    def save_metadata(
        self,
        image_id: str,
        metadata: ImageMetadata
    ) -> None:
        """Save metadata for the uploaded image."""
        image_dir = self.create_image_dir(image_id)

        metadata_path = image_dir / "metadata.json"

        print(f"[{image_id}] [{self.log_block}] Metadata image {image_id} saved in {metadata_path}")
        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(
                metadata.model_dump(),
                file,
                indent=4,
            )

    def get_current_image(self, image_id: str) -> Path:
        """Get the path to the current image."""
        metadata = self.load_metadata(image_id=image_id)
        current_ver = metadata.current_version
        version = metadata.versions[current_ver]

        return self.get_image_dir(image_id=image_id) / version.file

    def get_next_ver(self, image_id: str) -> int:
        """Get the next image version based on the current version."""
        metadata = self.load_metadata(image_id=image_id)
        current_ver = metadata.current_version
        return current_ver + 1

    def inspect_image(self, image_path: Path) -> ImageInfo:
        """Inspect the image and return its information."""
        with Image.open(image_path) as image:
            w, h = image.size
            frames = getattr(image, "n_frames", 1)
            image_format = image.format

        return ImageInfo(
            format=image_format,
            height=h,
            width=w,
            frames=frames
        )
    
    def save_version(self,image_id:str, image:Image,operation:str)->int:
        """Save current version based on the modification"""
        metadata = self.load_metadata(image_id=image_id)
        version = self.get_next_ver(image_id=image_id)
        current_image = self.get_current_image(image_id=image_id)

        extension = current_image.suffix
        filename = f"v{version:03d}{extension}"
        output_path = self.get_image_dir(image_id=image_id) / filename
        if extension.lower() in [".jpg", ".jpeg"]:
            if image.mode in ["RGBA", "LA"]:
                image = image.convert("RGB")
                        
        if extension.lower() == ".gif":
            gif_image = image.resized_frames
            gif_image[0].save(
                output_path,
                save_all=True,
                append_images=gif_image[1:],
                durations = image.durations,
                loop = image.loop
            )
            width = gif_image[0].width
            height = gif_image[0].height
            frames = len(gif_image)
            
        else:
            image.save(output_path)
            width = image.width
            height = image.height
            frames = getattr(image, "n_frames", 1)
            
        new_version = ImageVersion(
            version = version,
            file= filename,
            operation= operation,
            format = metadata.versions[metadata.current_version].format,
            width = width,
            height = height,
            frames = frames
        )
        metadata.versions.append(new_version)
        metadata.current_version = version
        self.save_metadata(image_id=image_id,metadata=metadata)
        print(f"[{image_id}] [{self.log_block}] Save Version for image {image_id} | Version {version}")
        return version
    
"""
load metadata
     ↓
get version 1
     ↓
create v001.gif
     ↓
save v001.gif
     ↓
create ImageVersion
     ↓
append to metadata.versions
     ↓
current_version = 1
     ↓
save metadata.json
     ↓
return 1
"""