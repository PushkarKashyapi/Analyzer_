import os
from pathlib import Path

import cv2
import pytesseract
from PIL import Image
from pytesseract import TesseractNotFoundError

# Windows Local Path
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


class OCRService:
    @classmethod
    def extract_text(cls, file_path: Path) -> str:
        """
        Extract text using Tesseract.
        If Tesseract is unavailable (Render), return empty string.
        """

        try:
            image = cv2.imread(str(file_path))

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            processed = cv2.threshold(
                gray, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )[1]

            return pytesseract.image_to_string(
                processed,
                lang="eng",
                config="--oem 3 --psm 6"
            )

        except TesseractNotFoundError:
            print("⚠️ Tesseract not available. Skipping OCR.")
            return ""

        except Exception as e:
            print("OCR Error:", e)
            return ""
