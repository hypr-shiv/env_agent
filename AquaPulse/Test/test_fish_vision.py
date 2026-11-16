import os
import io
import sys
import unittest
import asyncio
from PIL import Image, ImageDraw

# Configure UTF-8 encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.vision.preprocessor import (
    validate_image_file,
    preprocess_image,
    ImagePreprocessingError,
    ALLOWED_MIME_TYPES
)
from app.vision.classifier import AquaPulseFishClassifier, CONFIDENCE_THRESHOLD
from app.vision.species_catalog import VISION_SPECIES_CLASSES, SPECIES_BIOLOGY_DATA
from app.vision.service import FishVisionService, fish_vision_service
from app.api.v1.endpoints.vision import classify_fish_image, get_supported_species, get_model_info
from app.db.seed_data import seed_palghar_data_sync

def create_synthetic_image(
    format: str = "JPEG",
    size: tuple = (300, 200),
    color: tuple = (200, 210, 220),
    draw_pattern: str = "pomfret"
) -> bytes:
    """Creates a synthetic test image binary using Pillow."""
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)

    if draw_pattern == "pomfret":
        # Draw silvery diamond shape with fin
        draw.polygon([(50, 100), (150, 30), (250, 100), (150, 170)], fill=(225, 230, 240), outline=(180, 190, 200))
        draw.ellipse([(180, 80), (200, 95)], fill=(40, 40, 40))
    elif draw_pattern == "bombil":
        # Elongated slender fish
        draw.rectangle([20, 90, 280, 115], fill=(210, 215, 215), outline=(170, 175, 180))
        draw.polygon([(260, 90), (290, 75), (290, 130), (260, 115)], fill=(190, 195, 200))
    elif draw_pattern == "blank":
        # Solid flat color (low entropy)
        pass

    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()

def run_coro(coro):
    """Executes coroutine synchronously without OS socket dependency."""
    while True:
        try:
            coro.send(None)
        except StopIteration as e:
            return e.value

class TestAquaPulseFishVision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Seed baseline database records for market price retrieval."""
        seed_palghar_data_sync()
        cls.classifier = AquaPulseFishClassifier()
        cls.service = FishVisionService()

    def test_01_allowed_formats_validation(self):
        """Test valid JPEG, PNG, WEBP images pass validation."""
        for fmt, mime in [("JPEG", "image/jpeg"), ("PNG", "image/png"), ("WEBP", "image/webp")]:
            img_bytes = create_synthetic_image(format=fmt)
            # Should not raise exception
            validate_image_file(img_bytes, filename=f"test.{fmt.lower()}", content_type=mime)

    def test_02_rejection_of_empty_and_corrupt_files(self):
        """Test rejection of empty or non-image corrupted files."""
        # Empty file
        with self.assertRaises(ImagePreprocessingError):
            validate_image_file(b"", filename="empty.jpg", content_type="image/jpeg")

        # Corrupt bytes
        with self.assertRaises(ImagePreprocessingError):
            validate_image_file(b"NOT_A_VALID_IMAGE_BINARY_DATA", filename="fake.jpg", content_type="image/jpeg")

    def test_03_rejection_of_unsupported_format(self):
        """Test rejection of unsupported mime types."""
        img_bytes = create_synthetic_image(format="JPEG")
        with self.assertRaises(ImagePreprocessingError):
            validate_image_file(img_bytes, filename="data.pdf", content_type="application/pdf")

    def test_04_preprocessor_tensor_dimensions_and_normalization(self):
        """Test image preprocessor produces correct PyTorch tensor."""
        img_bytes = create_synthetic_image(format="JPEG", size=(400, 300))
        tensor, pil_img, meta = preprocess_image(img_bytes, filename="test.jpg", content_type="image/jpeg")

        self.assertEqual(tensor.shape, (1, 3, 224, 224))
        self.assertEqual(pil_img.mode, "RGB")
        self.assertIn("aspect_ratio", meta)
        self.assertIn("entropy", meta)

    def test_05_mobilenet_classification_returns_top_predictions(self):
        """Test MobileNetV3 classifier outputs predictions with confidence scores."""
        img_bytes = create_synthetic_image(format="JPEG", draw_pattern="pomfret")
        tensor, pil_img, meta = preprocess_image(img_bytes, filename="pomfret.jpg")

        result = self.classifier.classify_tensor(tensor, pil_img, meta)

        self.assertIn("predicted_species", result)
        self.assertIn("confidence", result)
        self.assertIn("alternative_predictions", result)
        self.assertIsInstance(result["alternative_predictions"], list)
        self.assertLessEqual(len(result["alternative_predictions"]), 2)
        self.assertGreater(result["confidence"], 0.0)

    def test_06_uncertainty_handling_never_force_prediction(self):
        """Test that low-information or ambiguous images trigger unknown/low confidence without forcing a guess."""
        blank_bytes = create_synthetic_image(format="JPEG", color=(255, 255, 255), draw_pattern="blank")
        tensor, pil_img, meta = preprocess_image(blank_bytes, filename="blank.jpg")

        result = self.classifier.classify_tensor(tensor, pil_img, meta)

        self.assertTrue(result["is_uncertain"])
        self.assertEqual(result["predicted_species"], "Unknown / Low Confidence")
        self.assertTrue(any("uncertain" in w.lower() or "insufficient" in w.lower() for w in result["warnings"]))

    def test_07_service_enriches_with_fisheries_and_market_data(self):
        """Test end-to-end service enriches prediction with biological & market price data."""
        img_bytes = create_synthetic_image(format="JPEG", draw_pattern="pomfret")
        response = self.service.process_and_classify(img_bytes, filename="specimen.jpg", content_type="image/jpeg")

        # Verify all mandatory schema keys
        expected_keys = [
            "predicted_species", "scientific_name", "local_name", "confidence",
            "alternative_predictions", "habitat", "seasonal_information",
            "local_distribution", "market_prices", "price_source", "price_date", "warnings"
        ]
        for key in expected_keys:
            self.assertIn(key, response, f"Missing key in vision response: {key}")

        # If confident, verify biology and prices
        if response["predicted_species"] != "Unknown / Low Confidence":
            self.assertNotEqual(response["scientific_name"], "")
            self.assertNotEqual(response["local_name"], "")
            self.assertIsInstance(response["seasonal_information"], dict)
            self.assertIsInstance(response["local_distribution"], list)
            self.assertIsInstance(response["market_prices"], list)
            self.assertGreater(len(response["market_prices"]), 0)

    def test_08_service_handles_uncertain_specimen_honestly(self):
        """Test service returns honest caveats for uncertain specimen without fabricating biology or price."""
        blank_bytes = create_synthetic_image(format="JPEG", color=(0, 0, 0), draw_pattern="blank")
        response = self.service.process_and_classify(blank_bytes, filename="blank.jpg", content_type="image/jpeg")

        self.assertEqual(response["predicted_species"], "Unknown / Low Confidence")
        self.assertEqual(response["market_prices"], [])
        self.assertGreater(len(response["warnings"]), 0)

    def test_09_supported_species_endpoint(self):
        """Test GET /api/v1/vision/species endpoint."""
        res = run_coro(get_supported_species())
        self.assertIn("supported_species", res)
        self.assertEqual(res["count"], len(VISION_SPECIES_CLASSES))

    def test_10_model_info_endpoint(self):
        """Test GET /api/v1/vision/model-info endpoint."""
        res = run_coro(get_model_info())
        self.assertEqual(res["model_architecture"], "MobileNetV3-Small")
        self.assertEqual(res["confidence_threshold"], CONFIDENCE_THRESHOLD)

    def test_11_gemma_vision_analysis_abundance_and_market_prices(self):
        """Test Gemma/PaliGemma extraction provides detailed biology, abundant areas, and market prices."""
        from app.vision.gemma_vision import gemma_vision_engine
        img_bytes = create_synthetic_image(format="JPEG", draw_pattern="pomfret")
        tensor, pil_img, meta = preprocess_image(img_bytes, filename="pomfret.jpg")

        res = gemma_vision_engine.analyze_fish_image(
            image_bytes=img_bytes,
            pil_img=pil_img,
            metadata=meta
        )

        self.assertIn("engine", res)
        self.assertIn("detailed_description", res)
        self.assertIn("abundance_information", res)
        self.assertIn("market_prices", res)
        self.assertIn("abundant_areas", res["abundance_information"])
        self.assertIn("summary", res["abundance_information"])
        self.assertGreater(len(res["abundance_information"]["abundant_areas"]), 0)

    def test_12_gemma_vision_uncertainty_rejection(self):
        """Test Gemma/PaliGemma rejects blank or unidentifiable specimen without fabricating data."""
        from app.vision.gemma_vision import gemma_vision_engine
        blank_bytes = create_synthetic_image(format="JPEG", color=(0, 0, 0), draw_pattern="blank")
        tensor, pil_img, meta = preprocess_image(blank_bytes, filename="blank.jpg")

        res = gemma_vision_engine.analyze_fish_image(
            image_bytes=blank_bytes,
            pil_img=pil_img,
            metadata=meta
        )

        self.assertEqual(res["predicted_species"], "Unknown / Low Confidence")
        self.assertEqual(res["abundance_information"]["abundant_areas"], [])
        self.assertEqual(res["market_prices"], [])
        self.assertGreater(len(res["warnings"]), 0)

if __name__ == "__main__":
    unittest.main()

