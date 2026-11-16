"""
AquaPulse Fish Vision Image Preprocessor.
Performs format validation, size constraints, integrity verification,
and PyTorch tensor transformation for MobileNetV3.
"""

import io
import math
import logging
from typing import Tuple, Dict, Any, Optional
from PIL import Image, ImageOps
import torch
import torchvision.transforms as transforms

logger = logging.getLogger("aquapulse.vision.preprocessor")

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_FILE_SIZE_BYTES = 100               # 100 Bytes

# Standard PyTorch normalization for MobileNetV3 / ImageNet
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def get_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize((224, 224), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

class ImagePreprocessingError(ValueError):
    """Raised when an uploaded image fails validation or processing."""
    pass

def validate_image_file(
    file_bytes: bytes,
    filename: Optional[str] = None,
    content_type: Optional[str] = None
) -> None:
    """
    Validates file size, MIME type / extension, and binary integrity.
    """
    # 1. Size Validation
    size = len(file_bytes)
    if size < MIN_FILE_SIZE_BYTES:
        raise ImagePreprocessingError(f"Image file too small or empty ({size} bytes). Minimum required is {MIN_FILE_SIZE_BYTES} bytes.")
    if size > MAX_FILE_SIZE_BYTES:
        raise ImagePreprocessingError(f"Image file exceeds maximum allowable size of 10MB ({size / (1024*1024):.2f}MB).")

    # 2. Content Type Validation
    if content_type and content_type.lower() not in ALLOWED_MIME_TYPES:
        # Check filename extension as fallback
        valid_ext = filename and any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
        if not valid_ext:
            raise ImagePreprocessingError(
                f"Unsupported image format '{content_type}'. Supported formats are: JPEG, PNG, WEBP."
            )

    # 3. Binary & Pillow Integrity Validation
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
    except Exception as e:
        raise ImagePreprocessingError(f"Invalid or corrupted image binary: {str(e)}")

def preprocess_image(
    file_bytes: bytes,
    filename: Optional[str] = None,
    content_type: Optional[str] = None
) -> Tuple[torch.Tensor, Image.Image, Dict[str, Any]]:
    """
    Validates, loads, checks visual entropy, and converts the image to a normalized PyTorch tensor.
    Returns:
        tensor: Normalized PyTorch tensor of shape (1, 3, 224, 224)
        pil_image: RGB PIL image
        metadata: Image morphological properties (width, height, aspect_ratio, entropy, variance)
    """
    validate_image_file(file_bytes, filename=filename, content_type=content_type)

    # Re-open after verify (PIL requirement)
    try:
        pil_img = Image.open(io.BytesIO(file_bytes))
        pil_img = ImageOps.exif_transpose(pil_img)  # Correct camera rotation
        pil_img = pil_img.convert("RGB")
    except Exception as e:
        raise ImagePreprocessingError(f"Failed to decode image pixels into RGB format: {str(e)}")

    width, height = pil_img.size
    aspect_ratio = round(width / max(height, 1), 3)

    # Compute entropy and pixel variance to detect flat/blank or corrupted images
    gray = pil_img.convert("L")
    hist = gray.histogram()
    total_pixels = sum(hist)
    entropy = 0.0
    for count in hist:
        if count > 0:
            p = count / total_pixels
            entropy -= p * math.log2(p)

    metadata = {
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "entropy": round(entropy, 3),
        "is_low_information": entropy < 0.8  # Blank or solid color
    }

    transform = get_transform()
    tensor = transform(pil_img).unsqueeze(0)  # Shape: (1, 3, 224, 224)

    return tensor, pil_img, metadata

