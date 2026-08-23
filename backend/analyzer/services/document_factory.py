from pathlib import Path

from analyzer.services.ocr_service import OCRService
from analyzer.services.pdf_service import PDFService
from analyzer.services.ai_service import AIService


class DocumentFactory:

    IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
    PDF_EXTENSIONS = [".pdf"]

    @classmethod
    def extract_text(cls, file_path: Path):

        extension = file_path.suffix.lower()

        if extension in cls.PDF_EXTENSIONS:
            return PDFService.extract_text(file_path)

        if extension in cls.IMAGE_EXTENSIONS:

            text = OCRService.extract_text(file_path)

            # Render fallback
            if not text.strip():
                text = AIService.extract_text_from_image(file_path)

            return text

        raise ValueError("Unsupported file format.")
