from pathlib import Path

from analyzer.services.ai_service import AIService
from analyzer.services.ocr_service import OCRService
from analyzer.services.pdf_service import PDFService


class DocumentFactory:
    """
    Handles document/image text extraction.
    Uses Tesseract locally and Gemini Vision as a fallback on Render.
    """

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    PDF_EXTENSIONS = {".pdf"}

    @classmethod
    def extract_text(cls, file_path: Path) -> str:
        extension = file_path.suffix.lower().strip()

        # PDF → PyMuPDF
        if extension in cls.PDF_EXTENSIONS:
            return PDFService.extract_text(file_path)

        # Images → Tesseract first, Gemini fallback
        if extension in cls.IMAGE_EXTENSIONS:
            text = OCRService.extract_text(file_path)

            # If OCR returns nothing (Render without Tesseract)
            if not text or not text.strip():
                text = AIService.extract_text_from_image(str(file_path))

            return text.strip()

        raise ValueError(f"Unsupported file format: {extension}")
