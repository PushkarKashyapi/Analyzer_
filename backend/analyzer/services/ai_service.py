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

        except json.JSONDecodeError:
            logger.exception("Failed to parse Gemini JSON.")
            return {}

    # ==========================================================
    # OCR FALLBACK USING GEMINI VISION
    # ==========================================================

    @classmethod
    def extract_text_from_image(cls, image_path: str):

        image = Image.open(image_path)

        prompt = """
Extract every visible piece of text from this image.

Rules:
- Return plain text only.
- Preserve headings and line breaks.
- Do not summarize.
- If no text exists return an empty string.
"""

        try:
            response = cls.model.generate_content([prompt, image])
            return response.text.strip()

        except Exception as error:
            logger.exception(error)
            return ""

    # ==========================================================
    # COMPLETE IMAGE ANALYSIS (ONE GEMINI CALL)
    # ==========================================================

    @classmethod
    def analyze_complete_post(
        cls,
        image_path: str,
        extracted_text: str,
        image_metrics: dict,
    ):
        """
        Complete AI analysis for every uploaded image.
        """

        image = Image.open(image_path)

        prompt = f"""
You are a Senior Social Media Growth Strategist, Brand Designer and Instagram Content Reviewer.

Analyze BOTH the uploaded image and caption.

=================================================
VISIBLE OCR TEXT
=================================================
{extracted_text}

=================================================
IMAGE METRICS FROM OPENCV
=================================================
{json.dumps(image_metrics)}

=================================================
STEP 1 — PLATFORM DETECTION
=================================================

Identify the most suitable platform.

Possible values:
Instagram
LinkedIn
Facebook
Pinterest
X
Other

Also identify:

- target_audience
- post_goal

Goals:
Sales
Brand Awareness
Engagement
Education
Personal Sharing
Event Promotion

=================================================
STEP 2 — CONTENT CLASSIFICATION
=================================================

Return:

content_type

Possible values:

Marketing Poster
Product Promotion
Educational Carousel
Event Announcement
Selfie
Personal Photo
Travel Photo
Entertainment / Meme
Other

Also return:

business_category

Possible values:

Food
Fashion
Beauty
Technology
Healthcare
Education
Finance
Fitness
Real Estate
Travel
None
Other

=================================================
STEP 3 — IMAGE DETECTION
=================================================

Detect:

contains_text
contains_human
contains_product
logo_present
cta_found
cta_text

=================================================
STEP 4 — IF BUSINESS POSTER
=================================================

Evaluate:

- Brand color psychology.
- Color suitability.
- Color combination.
- Typography hierarchy.
- Font readability.
- CTA visibility.
- Text density.
- Whitespace.
- Thumbnail attractiveness.
- Visual hierarchy.

Explain WHY.

=================================================
STEP 5 — IF PERSONAL PHOTO / SELFIE / TRAVEL
=================================================

Evaluate:

- Lighting.
- Contrast.
- Saturation.
- Composition.
- Rule of thirds.
- Background cleanliness.
- Eye catchiness.
- Visual appeal.
- Editing suggestions.
- Thumbnail appeal.

=================================================
STEP 6 — CAPTION ANALYSIS
=================================================

Evaluate caption on platform basis.

Give scores (0-100):

hook_score
catchiness_score
engagement_score
readability_score
cta_score
emoji_score
hashtag_score

Also detect:

sentiment

=================================================
STEP 7 — GROWTH SUGGESTIONS
=================================================

Generate:

- Better hook.
- Better caption.
- CTA improvement.
- Reach tips.
- Best posting time.
- 10 hashtags.

=================================================
BUSINESS RULES
=================================================

Food:
Warm colors preferred.

Technology:
Blue / White / Black palette.

Beauty:
Soft luxury palette.

Fitness:
Green / Black / White.

Fashion:
Neutral or premium palette.

Selfie:
Ignore business rules.

=================================================
RETURN ONLY VALID JSON
=================================================

{{
  "platform":"",
  "target_audience":"",
  "post_goal":"",

  "content_type":"",
  "business_category":"",

  "contains_text":true,
  "contains_human":false,
  "contains_product":false,
  "logo_present":false,

  "cta_found":false,
  "cta_text":"",

  "marketing_analysis": {{
      "business_score":0,
      "color_alignment_score":0,
      "color_psychology_feedback":[],
      "text_density_score":0,
      "typography_score":0,
      "whitespace_score":0,
      "cta_visibility_score":0,
      "thumbnail_score":0,
      "strengths":[],
      "weaknesses":[],
      "business_feedback":[],
      "design_suggestions":[]
  }},

  "personal_analysis": {{
      "photo_score":0,
      "lighting_score":0,
      "composition_score":0,
      "eye_catchiness_score":0,
      "visual_appeal_score":0,
      "background_score":0,
      "strengths":[],
      "weaknesses":[],
      "photo_feedback":[],
      "editing_suggestions":[]
  }},

  "caption_analysis": {{
      "hook_score":0,
      "catchiness_score":0,
      "engagement_score":0,
      "readability_score":0,
      "cta_score":0,
      "emoji_score":0,
      "hashtag_score":0,
      "sentiment":"",
      "strengths":[],
      "weaknesses":[],
      "caption_suggestions":[],
      "reach_tips":[],
      "best_posting_time":"",
      "improved_caption":"",
      "hashtags":[]
  }}
}}
"""

        try:
            response = cls.model.generate_content(
                [prompt, image],
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )

            return cls.parse_json(response.text)

        except Exception as error:

            logger.exception(error)

            return {
                "platform": "Other",
                "target_audience": "",
                "post_goal": "",
                "content_type": "Other",
                "business_category": "None",
                "contains_text": False,
                "contains_human": False,
                "contains_product": False,
                "logo_present": False,
                "cta_found": False,
                "cta_text": "",
                "marketing_analysis": None,
                "personal_analysis": None,
                "caption_analysis": {
                    "hook_score": 0,
                    "catchiness_score": 0,
                    "engagement_score": 0,
                    "readability_score": 0,
                    "cta_score": 0,
                    "emoji_score": 0,
                    "hashtag_score": 0,
                    "sentiment": "Unknown",
                    "strengths": [],
                    "weaknesses": [],
                    "caption_suggestions": [],
                    "reach_tips": [],
                    "best_posting_time": "",
                    "improved_caption": extracted_text,
                    "hashtags": [],
                },
            }

    # ==========================================================
    # CAPTION ANALYSIS FOR PDF / TEXT ONLY
    # ==========================================================

    @classmethod
    def analyze_caption(
        cls,
        caption_text: str,
        content_type: str = "PDF",
        business_category: str = "None",
    ):

        prompt = f"""
You are a professional social media strategist.

Content Type:
{content_type}

Business Category:
{business_category}

Caption:
{caption_text}

Analyze this caption.

Return ONLY JSON.

{{
  "hook_score":0,
  "catchiness_score":0,
  "engagement_score":0,
  "readability_score":0,
  "cta_score":0,
  "emoji_score":0,
  "hashtag_score":0,
  "sentiment":"",
  "strengths":[],
  "weaknesses":[],
  "caption_suggestions":[],
  "reach_tips":[],
  "best_posting_time":"",
  "improved_caption":"",
  "hashtags":[]
}}
"""

        try:

            response = cls.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    response_mime_type="application/json",
                ),
            )

            return cls.parse_json(response.text)

        except Exception as error:

            logger.exception(error)

            return {
                "hook_score": 0,
                "catchiness_score": 0,
                "engagement_score": 0,
                "readability_score": 0,
                "cta_score": 0,
                "emoji_score": 0,
                "hashtag_score": 0,
                "sentiment": "Unknown",
                "strengths": [],
                "weaknesses": [],
                "caption_suggestions": [],
                "reach_tips": [],
                "best_posting_time": "",
                "improved_caption": caption_text,
                "hashtags": [],
            }
