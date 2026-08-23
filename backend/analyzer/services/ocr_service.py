import os
from pathlib import Path

import cv2
import pytesseract
from pytesseract import TesseractNotFoundError


# ----------------------------------------------------------
# Configure Tesseract Path
# ----------------------------------------------------------

if os.name == "nt":
    # Windows Local Development
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
else:
    # Linux / Docker / Render
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


class OCRService:
    """
    OCR Service using Tesseract OCR.

    Works on:
    - Windows (Local)
    - Docker / Render (Linux)
    """

    @classmethod
    def extract_text(cls, file_path: Path) -> str:
        """
        Extract text from an image using Tesseract OCR.
        """

        try:
            image = cv2.imread(str(file_path))

            if image is None:
                raise ValueError("Unable to read image for OCR.")

            processed_image = cls.preprocess_image(image)

            text = pytesseract.image_to_string(
                processed_image,
                lang="eng",
                config="--oem 3 --psm 6",
            )

            return text.strip()

        except TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract OCR is not installed or not found at the configured path."
            )

        except Exception as error:
            raise RuntimeError(f"OCR processing failed: {error}")

    # ----------------------------------------------------------
    # Image Preprocessing
    # ----------------------------------------------------------

    @staticmethod
    def preprocess_image(image):
        """
        Improve image quality before OCR.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Remove noise while preserving edges
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        # Increase contrast
        gray = cv2.equalizeHist(gray)

        # Binary threshold for cleaner text
        threshold = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]

        # Small morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

        return cleaned
