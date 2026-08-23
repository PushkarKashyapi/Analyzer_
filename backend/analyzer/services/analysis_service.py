from pathlib import Path

from analyzer.services.ai_service import AIService
from analyzer.services.document_factory import DocumentFactory
from analyzer.services.image_analysis_service import ImageAnalysisService


class AnalysisService:
    """
    Main orchestrator for the Social Media Content Analyzer.
    """

    IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}

    @classmethod
    def process_document(cls, file_path: Path, filename: str) -> dict:
        # ----------------------------------------------------
        # STEP 1 : Extract text (PDF / OCR / Gemini OCR fallback)
        # ----------------------------------------------------
        extracted_text = DocumentFactory.extract_text(file_path)

        # ----------------------------------------------------
        # STEP 2 : Default values
        # ----------------------------------------------------
        image_analysis = {}
        content_type = "Other"
        business_category = "None"
        marketing_analysis = None
        personal_analysis = None
        caption_analysis = {}

        # ----------------------------------------------------
        # STEP 3 : Image Pipeline
        # ----------------------------------------------------
        if file_path.suffix.lower() in cls.IMAGE_TYPES:

            # OpenCV metrics
            image_analysis = ImageAnalysisService.analyze(file_path)

            # -------- SINGLE GEMINI CALL --------
            ai_result = AIService.analyze_complete_post(
                image_path=str(file_path),
                extracted_text=extracted_text,
                image_metrics=image_analysis,
            )

            content_type = ai_result.get("content_type", "Other")
            business_category = ai_result.get("business_category", "None")

            marketing_analysis = ai_result.get("marketing_analysis")
            personal_analysis = ai_result.get("personal_analysis")
            caption_analysis = ai_result.get("caption_analysis", {})

        # ----------------------------------------------------
        # STEP 4 : PDF/Text Pipeline
        # ----------------------------------------------------
        else:
            caption_analysis = AIService.analyze_caption(
                caption_text=extracted_text,
                content_type="PDF",
                business_category="None",
            )

        # ----------------------------------------------------
        # STEP 5 : Overall Score
        # ----------------------------------------------------
        overall_score = cls.calculate_overall_score(
            image_metrics=image_analysis,
            marketing_analysis=marketing_analysis,
            personal_analysis=personal_analysis,
            caption_analysis=caption_analysis,
        )

        # ----------------------------------------------------
        # STEP 6 : Final Response
        # ----------------------------------------------------
        return {
            "filename": filename,

            "content_type": content_type,
            "business_category": business_category,

            "overall_score": overall_score,

            "characters": len(extracted_text),
            "words": len(extracted_text.split()),
            "extracted_text": extracted_text,

            "image_analysis": image_analysis,
            "marketing_analysis": marketing_analysis,
            "personal_analysis": personal_analysis,
            "caption_analysis": caption_analysis,
        }

    # ========================================================
    # Overall Score Calculation (Deterministic)
    # ========================================================

    @staticmethod
    def calculate_overall_score(
        image_metrics,
        marketing_analysis,
        personal_analysis,
        caption_analysis,
    ):
        """
        Overall score is calculated in Python (not AI generated).
        """

        caption_score = (
            caption_analysis.get("engagement_score", 0)
            + caption_analysis.get("catchiness_score", 0)
            + caption_analysis.get("readability_score", 0)
        ) / 3

        # -------- Marketing Posts --------
        if marketing_analysis:

            business_score = marketing_analysis.get("business_score", 0)

            visual_score = (
                image_metrics.get("brightness_score", 0)
                + image_metrics.get("contrast_score", 0)
                + image_metrics.get("color_harmony_score", 0)
                + image_metrics.get("sharpness_score", 0)
            ) / 4

            score = (
                business_score * 0.40
                + caption_score * 0.35
                + visual_score * 0.25
            )

            return round(score)

        # -------- Personal / Selfie / Travel --------
        if personal_analysis:

            photo_score = personal_analysis.get("photo_score", 0)

            visual_score = (
                image_metrics.get("brightness_score", 0)
                + image_metrics.get("contrast_score", 0)
                + image_metrics.get("sharpness_score", 0)
                + image_metrics.get("color_harmony_score", 0)
            ) / 4

            score = (
                photo_score * 0.50
                + visual_score * 0.20
                + caption_score * 0.30
            )

            return round(score)

        # -------- PDF / Text Only --------
        return round(caption_score)
