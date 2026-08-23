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
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)


class AIService:
    """
    Handles all Gemini AI operations.

    1. OCR fallback (Gemini Vision)
    2. Detect content type.
    3. Analyze marketing posters.
    4. Analyze personal/selfie/travel images.
    5. Analyze captions.
    """

    model = genai.GenerativeModel("gemini-3.6-flash")

    # ---------------------------------------------------------
    # Helper
    # ---------------------------------------------------------

    @classmethod
    def _parse_json(cls, response_text: str):
        cleaned = (
            response_text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(cleaned)

    # ---------------------------------------------------------
    # OCR FALLBACK USING GEMINI VISION (NEW)
    # ---------------------------------------------------------

    @classmethod
    def extract_text_from_image(cls, image_path: str):
        """
        Used only when Tesseract is unavailable (Render deployment).
        Extracts visible text using Gemini Vision.
        """

        image = Image.open(image_path)

        prompt = """
Extract every piece of visible text from this image.

Rules:
- Return plain text only.
- Preserve headings and line breaks.
- Do not explain anything.
- If no text exists, return an empty string.
"""

        try:
            response = cls.model.generate_content([prompt, image])
            return response.text.strip()

        except Exception as error:
            logger.exception(error)
            return ""

    # ---------------------------------------------------------
    # STEP 1 : Detect Content Type
    # ---------------------------------------------------------

    @classmethod
    def detect_content_type(cls, image_path: str):

        image = Image.open(image_path)

        prompt = """
You are an AI social media classifier.

Look at this image.

Return ONLY valid JSON.

{
    "content_type": "",
    "business_category": "",
    "contains_text": true,
    "contains_human": false,
    "contains_product": false,
    "target_platform": ""
}

content_type MUST be one of:
- Marketing Poster
- Product Promotion
- Educational Post
- Personal Photo
- Selfie
- Travel Photo
- Entertainment / Meme
- Event Announcement
- Other

business_category examples:
Food
Fashion
Technology
Beauty
Healthcare
Finance
Fitness
Travel
Education
Real Estate
None
"""

        try:
            response = cls.model.generate_content([prompt, image])
            return cls._parse_json(response.text)

        except Exception as error:
            logger.exception(error)

            return {
                "content_type": "Other",
                "business_category": "None",
                "contains_text": False,
                "contains_human": False,
                "contains_product": False,
                "target_platform": "Instagram",
            }

    # ---------------------------------------------------------
    # STEP 2A : Marketing Poster Analysis
    # ---------------------------------------------------------

    @classmethod
    def analyze_marketing_image(
        cls,
        image_path: str,
        caption_text: str,
        image_metrics: dict,
        business_category: str,
    ):

        image = Image.open(image_path)

        prompt = f"""
You are a branding and marketing expert.

Business Category:
{business_category}

Image Metrics:
{json.dumps(image_metrics)}

Caption:
{caption_text}

Analyze ONLY from marketing perspective.

Return ONLY JSON.

{{
  "business_score":0,
  "color_alignment_score":0,
  "text_density_score":0,
  "typography_score":0,
  "cta_visibility_score":0,

  "strengths":[],
  "weaknesses":[],
  "business_feedback":[],
  "design_suggestions":[]
}}
"""

        try:
            response = cls.model.generate_content([prompt, image])
            return cls._parse_json(response.text)

        except Exception as error:
            logger.exception(error)

            return {
                "business_score": 0,
                "color_alignment_score": 0,
                "text_density_score": 0,
                "typography_score": 0,
                "cta_visibility_score": 0,
                "strengths": [],
                "weaknesses": [],
                "business_feedback": [],
                "design_suggestions": [],
            }

    # ---------------------------------------------------------
    # STEP 2B : Personal / Selfie / Travel Analysis
    # ---------------------------------------------------------

    @classmethod
    def analyze_personal_image(
        cls,
        image_path: str,
        caption_text: str,
        image_metrics: dict,
    ):

        image = Image.open(image_path)

        prompt = f"""
You are an Instagram photographer and content creator.

Image Metrics:
{json.dumps(image_metrics)}

Caption:
{caption_text}

Analyze this image ONLY as a personal/social media photo.

Focus on:
- Eye catchiness.
- Composition.
- Color harmony.
- Lighting.
- Contrast.
- Saturation.
- Visual appeal.

Return ONLY JSON.

{{
  "photo_score":0,
  "eye_catchiness_score":0,
  "composition_score":0,
  "visual_appeal_score":0,

  "strengths":[],
  "weaknesses":[],
  "photo_feedback":[],
  "editing_suggestions":[]
}}
"""

        try:
            response = cls.model.generate_content([prompt, image])
            return cls._parse_json(response.text)

        except Exception as error:
            logger.exception(error)

            return {
                "photo_score": 0,
                "eye_catchiness_score": 0,
                "composition_score": 0,
                "visual_appeal_score": 0,
                "strengths": [],
                "weaknesses": [],
                "photo_feedback": [],
                "editing_suggestions": [],
            }

    # ---------------------------------------------------------
    # STEP 3 : Caption Analysis
    # ---------------------------------------------------------

    @classmethod
    def analyze_caption(
        cls,
        caption_text: str,
        content_type: str,
        business_category: str,
    ):

        prompt = f"""
You are a professional social media strategist.

Content Type:
{content_type}

Business Category:
{business_category}

Caption:
{caption_text}

Analyze caption for engagement.

Return ONLY JSON.

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
            return cls._parse_json(response.text)

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
