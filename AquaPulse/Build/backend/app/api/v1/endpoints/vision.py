"""
AquaPulse Fish Vision API Endpoints.
Provides image upload, MobileNetV3 classification, and cross-agent enrichment.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Dict, Any, List

from app.vision.service import fish_vision_service
from app.vision.gemma_vision import gemma_vision_engine
from app.vision.preprocessor import ImagePreprocessingError, preprocess_image
from app.vision.species_catalog import VISION_SPECIES_CLASSES, SPECIES_BIOLOGY_DATA
from app.vision.classifier import CONFIDENCE_THRESHOLD

logger = logging.getLogger("aquapulse.api.vision")

router = APIRouter(prefix="/vision", tags=["Fish Vision & Species Identification"])

@router.post(
    "/classify",
    summary="Identify Fish Species from Image",
    description="Uploads an image, classifies fish species with MobileNetV3, and queries Fisheries and Market agents for biological data and live auction prices."
)
async def classify_fish_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Accepts multipart/form-data image upload.
    Validates format, size, and integrity.
    Executes MobileNetV3 inference with uncertainty rejection.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided in upload request."
        )

    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes)."
            )

        result = fish_vision_service.process_and_classify(
            image_bytes=image_bytes,
            filename=file.filename,
            content_type=file.content_type
        )
        return result

    except ImagePreprocessingError as e:
        logger.warning(f"Image preprocessing rejection: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Fish vision classification internal error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the fish image: {str(e)}"
        )

@router.post(
    "/gemma-analyze",
    summary="Detailed Fish Extraction with Gemma / PaliGemma Vision",
    description="Uploads an image, applies Google's Gemma / PaliGemma multimodal extraction, and returns detailed species taxonomy, abundance zones in Palghar, and live market prices."
)
async def gemma_analyze_fish_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided in upload request."
        )

    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes)."
            )

        tensor, pil_img, metadata = preprocess_image(
            file_bytes=image_bytes,
            filename=file.filename,
            content_type=file.content_type
        )

        result = gemma_vision_engine.analyze_fish_image(
            image_bytes=image_bytes,
            pil_img=pil_img,
            metadata=metadata
        )
        return result

    except ImagePreprocessingError as e:
        logger.warning(f"Image preprocessing rejection: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Gemma fish vision internal error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during Gemma vision extraction: {str(e)}"
        )

@router.get(
    "/species",
    summary="List Supported Fish Species",
    description="Returns the verified catalog of Palghar marine fish species supported by the vision classifier."
)
async def get_supported_species() -> Dict[str, Any]:
    catalog_list = []
    for sp in VISION_SPECIES_CLASSES:
        bio = SPECIES_BIOLOGY_DATA.get(sp, {})
        catalog_list.append({
            "species_name": sp,
            "scientific_name": bio.get("scientific_name", ""),
            "local_name": bio.get("local_name", ""),
            "commercial_tier": bio.get("commercial_tier", "Commercial")
        })
    return {
        "count": len(catalog_list),
        "supported_species": catalog_list
    }

@router.get(
    "/model-info",
    summary="Vision Model Architecture & Configuration",
    description="Returns details regarding the MobileNetV3 architecture, input constraints, and safety thresholds."
)
async def get_model_info() -> Dict[str, Any]:
    return {
        "model_architecture": "MobileNetV3-Small",
        "input_resolution": "224x224 RGB",
        "num_classes": len(VISION_SPECIES_CLASSES),
        "target_classes": VISION_SPECIES_CLASSES,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "uncertainty_policy": "Never force a species prediction when uncertain. Low-confidence triggers rejection."
    }

