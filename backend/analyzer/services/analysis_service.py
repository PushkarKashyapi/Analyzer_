from pathlib import Path

from analyzer.services.ai_service import AIService
from analyzer.services.document_factory import DocumentFactory
from analyzer.services.image_analysis_service import ImageAnalysisService


class AnalysisService:
    """
    Main orchestrator for the Social Media Content Analyzer.

    Flow:
    1. OCR / PDF Text Extraction.
    2. OpenCV Image Metrics.
    3. Gemini Vision Analysis.
    4. Deterministic Overall Score.
    """

    IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}

    @classmethod
    def process_document(cls, file_path: Path, filename: str):
        # ----------------------------------------------------
        # STEP 1 : Extract text
        # ----------------------------------------------------
        extracted_text = DocumentFactory.extract_text(file_path)

        # ----------------------------------------------------
        # STEP 2 : Defaults
        # ----------------------------------------------------
        image_analysis = {}
        ai_result = {}

        platform = "Other"
        content_type = "Other"
        business_category = "None"
        target_audience = ""
        post_goal = ""

        marketing_analysis = None
        personal_analysis = None
        caption_analysis = {}

        # ----------------------------------------------------
        # STEP 3 : Image Pipeline
        # ----------------------------------------------------
        if file_path.suffix.lower() in cls.IMAGE_TYPES:

            image_analysis = ImageAnalysisService.analyze(file_path)

            ai_result = AIService.analyze_complete_post(
                image_path=str(file_path),
                extracted_text=extracted_text,
                image_metrics=image_analysis,
            )

            platform = ai_result.get("platform", "Other")
            content_type = ai_result.get("content_type", "Other")
            business_category = ai_result.get("business_category", "None")
            target_audience = ai_result.get("target_audience", "")
            post_goal = ai_result.get("post_goal", "")

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
        # STEP 6 : Overall Grade
        # ----------------------------------------------------
        if overall_score >= 90:
            grade = "Excellent"
        elif overall_score >= 75:
            grade = "Good"
        elif overall_score >= 60:
            grade = "Average"
        else:
            grade = "Needs Improvement"

        # ----------------------------------------------------
        # STEP 7 : Final API Response
        # ----------------------------------------------------
        return {
            "filename": filename,

            # Classification
            "platform": platform,
            "content_type": content_type,
            "business_category": business_category,
            "target_audience": target_audience,
            "post_goal": post_goal,

            # Final Rating
            "overall_score": overall_score,
            "overall_grade": grade,

            # OCR Information
            "characters": len(extracted_text),
            "words": len(extracted_text.split()),
            "extracted_text": extracted_text,

            # Image Metrics (OpenCV)
            "image_analysis": image_analysis,

            # AI Results
            "marketing_analysis": marketing_analysis,
            "personal_analysis": personal_analysis,
            "caption_analysis": caption_analysis,
        }

    # =========================================================
    # Deterministic Overall Score
    # =========================================================

    @staticmethod
    def calculate_overall_score(
        image_metrics,
        marketing_analysis,
        personal_analysis,
        caption_analysis,
    ):
        """
        Overall score is calculated in Python instead of Gemini.
        This keeps scoring consistent across requests.
        """

        # ---------------- Caption Score ----------------
        caption_score = (
            caption_analysis.get("hook_score", 0) * 0.20
            + caption_analysis.get("catchiness_score", 0) * 0.20
            + caption_analysis.get("engagement_score", 0) * 0.25
            + caption_analysis.get("readability_score", 0) * 0.15
            + caption_analysis.get("cta_score", 0) * 0.10
            + caption_analysis.get("emoji_score", 0) * 0.05
            + caption_analysis.get("hashtag_score", 0) * 0.05
        )

        # ---------------- Common Visual Score ----------------
        visual_score = (
            image_metrics.get("brightness_score", 0)
            + image_metrics.get("contrast_score", 0)
            + image_metrics.get("sharpness_score", 0)
            + image_metrics.get("color_harmony_score", 0)
            + image_metrics.get("color_balance_score", 0)
        ) / 5

        # =====================================================
        # MARKETING / BUSINESS POSTS
        # =====================================================
        if marketing_analysis:

            business_score = (
                marketing_analysis.get("business_score", 0) * 0.30
                + marketing_analysis.get("color_alignment_score", 0) * 0.15
                + marketing_analysis.get("typography_score", 0) * 0.10
                + marketing_analysis.get("text_density_score", 0) * 0.10
                + marketing_analysis.get("whitespace_score", 0) * 0.05
                + marketing_analysis.get("cta_visibility_score", 0) * 0.15
                + marketing_analysis.get("thumbnail_score", 0) * 0.15
            )

            score = (
                business_score * 0.45
                + caption_score * 0.30
                + visual_score * 0.25
            )

            return min(round(score), 100)

        # =====================================================
        # SELFIE / PERSONAL / TRAVEL POSTS
        # =====================================================
        if personal_analysis:

            photo_score = (
                personal_analysis.get("photo_score", 0) * 0.25
                + personal_analysis.get("lighting_score", 0) * 0.15
                + personal_analysis.get("composition_score", 0) * 0.15
                + personal_analysis.get("eye_catchiness_score", 0) * 0.20
                + personal_analysis.get("visual_appeal_score", 0) * 0.15
                + personal_analysis.get("background_score", 0) * 0.10
            )

            score = (
                photo_score * 0.50
                + caption_score * 0.30
                + visual_score * 0.20
            )

            return min(round(score), 100)

        # =====================================================
        # PDF / TEXT ONLY
        # =====================================================
        return min(round(caption_score), 100)
