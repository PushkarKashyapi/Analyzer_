import json
import logging
import os

import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

genai.configure(api_key=api_key)


class AIService:
    """
    AI Service for Social Media Content Analyzer.

    Features:
    1. Gemini Vision OCR fallback.
    2. Complete image + caption analysis in ONE Gemini request.
    3. Caption-only analysis for PDFs.
    """

    model = genai.GenerativeModel("gemini-3.6-flash")

    # ==========================================================
    # Helper
    # ==========================================================

    @classmethod
    def parse_json(cls, response_text: str):
        cleaned = (
            response_text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            return json.loads(cleaned)
        except Exception:
            logger.exception("Failed to parse Gemini JSON.")
            return {}

    # ==========================================================
    # OCR FALLBACK (Gemini Vision)
    # ==========================================================

    @classmethod
    def extract_text_from_image(cls, image_path: str):
        image = Image.open(image_path)

        prompt = """
Extract all visible text from this image.

Rules:
- Return plain text only.
- Preserve headings and line breaks.
- If no text exists, return an empty string.
"""

        try:
            response = cls.model.generate_content([prompt, image])
            return response.text.strip()

        except Exception as error:
            logger.exception(error)
            return ""

    # ==========================================================
    # COMPLETE IMAGE + CAPTION ANALYSIS (ONE GEMINI CALL)
    # ==========================================================

    @classmethod
    def analyze_complete_post(
        cls,
        image_path: str,
        extracted_text: str,
        image_metrics: dict,
    ):
        """
        One Gemini Vision call for complete analysis.
        """

        image = Image.open(image_path)

        prompt = f"""
You are an expert Instagram, LinkedIn and marketing strategist.

Analyze this uploaded social media image.

Visible OCR Text:
{extracted_text}

Image Metrics:
{json.dumps(image_metrics)}

Your job:

STEP 1 — Detect post type.

Possible content types:
- Marketing Poster
- Product Promotion
- Educational Post
- Event Announcement
- Selfie
- Personal Photo
- Travel Photo
- Entertainment / Meme
- Other

STEP 2 — Detect business category.
Examples:
Food, Fashion, Beauty, Healthcare, Technology,
Fitness, Travel, Education, Finance, Real Estate, None.

STEP 3 — If it's a marketing/business poster:
- Color psychology.
- Color combination.
- Brand consistency.
- Typography.
- CTA visibility.
- Text density.
- Layout hierarchy.

STEP 4 — If it's a selfie/personal/travel photo:
- Lighting.
- Composition.
- Eye catchiness.
- Color harmony.
- Contrast.
- Visual appeal.
- Editing suggestions.

STEP 5 — Analyze the caption/visible text:
- Engagement.
- Readability.
- Catchiness.
- CTA strength.
- Sentiment.

STEP 6 — Generate:
- Better caption.
- Trending hashtags.
- Reach improvement tips.

Return ONLY valid JSON.

{{
  "content_type":"",
  "business_category":"",
  "overall_score":0,

  "marketing_analysis":{{
      "business_score":0,
      "color_alignment_score":0,
      "text_density_score":0,
      "typography_score":0,
      "cta_visibility_score":0,
      "strengths":[],
      "weaknesses":[],
      "business_feedback":[],
      "design_suggestions":[]
  }},

  "personal_analysis":{{
      "photo_score":0,
      "eye_catchiness_score":0,
      "composition_score":0,
      "visual_appeal_score":0,
      "strengths":[],
      "weaknesses":[],
      "photo_feedback":[],
      "editing_suggestions":[]
  }},

  "caption_analysis":{{
      "catchiness_score":0,
      "engagement_score":0,
      "readability_score":0,
      "cta_score":0,
      "sentiment":"",
      "strengths":[],
      "weaknesses":[],
      "caption_suggestions":[],
      "reach_tips":[],
      "improved_caption":"",
      "hashtags":[]
  }}
}}
"""

        try:
            response = cls.model.generate_content([prompt, image])
            return cls.parse_json(response.text)

        except Exception as error:
            logger.exception(error)

            return {
                "content_type": "Other",
                "business_category": "None",
                "overall_score": 0,
                "marketing_analysis": None,
                "personal_analysis": None,
                "caption_analysis": {
                    "catchiness_score": 0,
                    "engagement_score": 0,
                    "readability_score": 0,
                    "cta_score": 0,
                    "sentiment": "Unknown",
                    "strengths": [],
                    "weaknesses": [],
                    "caption_suggestions": [],
                    "reach_tips": [],
                    "improved_caption": extracted_text,
                    "hashtags": [],
                },
            }

    # ==========================================================
    # PDF / TEXT-ONLY CAPTION ANALYSIS
    # ==========================================================

    @classmethod
    def analyze_caption(
        cls,
        caption_text: str,
        content_type: str = "PDF",
        business_category: str = "None",
    ):
        """
        Used only for PDF uploads or text-only documents.
        """

        prompt = f"""
You are a professional social media strategist.

Content Type:
{content_type}

Business Category:
{business_category}

Caption:
{caption_text}

Return ONLY valid JSON.

{{
  "catchiness_score":0,
  "engagement_score":0,
  "readability_score":0,
  "cta_score":0,
  "sentiment":"",
  "strengths":[],
  "weaknesses":[],
  "caption_suggestions":[],
  "reach_tips":[],
  "improved_caption":"",
  "hashtags":[]
}}
"""

        try:
            response = cls.model.generate_content(prompt)
            return cls.parse_json(response.text)

        except Exception as error:
            logger.exception(error)

            return {
                "catchiness_score": 0,
                "engagement_score": 0,
                "readability_score": 0,
                "cta_score": 0,
                "sentiment": "Unknown",
                "strengths": [],
                "weaknesses": [],
                "caption_suggestions": [],
                "reach_tips": [],
                "improved_caption": caption_text,
                "hashtags": [],
            }
