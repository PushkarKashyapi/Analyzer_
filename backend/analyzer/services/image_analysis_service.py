from pathlib import Path

import cv2
import numpy as np
import pytesseract
from pytesseract import TesseractNotFoundError
from sklearn.cluster import KMeans


class ImageAnalysisService:
    """
    OpenCV-based image quality analysis service.

    Runs for EVERY uploaded image and provides metrics for:
    - Marketing posters
    - Selfies / Personal photos
    - Travel / Entertainment posts
    """

    @classmethod
    def analyze(cls, file_path: Path) -> dict:
        image = cv2.imread(str(file_path))

        if image is None:
            raise ValueError("Unable to read uploaded image.")

        return {
            # ---------- Image Quality ----------
            "brightness_score": cls.get_brightness(image),
            "contrast_score": cls.get_contrast(image),
            "sharpness_score": cls.get_sharpness(image),
            "saturation_score": cls.get_saturation(image),
            "exposure_score": cls.get_exposure(image),
            "noise_score": cls.get_noise(image),

            # ---------- Color Analysis ----------
            "dominant_colors": cls.get_dominant_colors(image),
            "color_harmony_score": cls.get_color_harmony(image),
            "color_balance_score": cls.get_color_balance(image),

            # ---------- Marketing Metrics ----------
            "whitespace_score": cls.get_whitespace(image),
            "text_density": cls.get_text_density(image),
        }

    # ==========================================================
    # IMAGE QUALITY METRICS
    # ==========================================================

    @staticmethod
    def get_brightness(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        return round((brightness / 255) * 100)

    @staticmethod
    def get_contrast(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray)
        return round(min((contrast / 128) * 100, 100))

    @staticmethod
    def get_sharpness(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        score = min((variance / 500) * 100, 100)
        return round(score)

    @staticmethod
    def get_saturation(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv[:, :, 1])
        return round((saturation / 255) * 100)

    @staticmethod
    def get_exposure(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean = np.mean(gray)
        score = 100 - abs(mean - 128) / 128 * 100
        return round(max(score, 0))

    @staticmethod
    def get_noise(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = np.mean(cv2.absdiff(gray, blurred))
        score = 100 - min(noise * 4, 100)
        return round(max(score, 0))

    # ==========================================================
    # COLOR ANALYSIS
    # ==========================================================

    @staticmethod
    def get_dominant_colors(image, clusters=3):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pixels = rgb.reshape((-1, 3))

        model = KMeans(
            n_clusters=clusters,
            random_state=42,
            n_init="auto",
        )

        model.fit(pixels)

        colors = []

        for color in model.cluster_centers_:
            colors.append(
                "#{:02X}{:02X}{:02X}".format(
                    int(color[0]),
                    int(color[1]),
                    int(color[2]),
                )
            )

        return colors

    @staticmethod
    def get_color_harmony(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        hue = hsv[:, :, 0].flatten()
        saturation = hsv[:, :, 1].flatten()

        # Ignore grayscale pixels
        hue = hue[saturation > 30]

        if len(hue) == 0:
            return 50

        variance = np.std(hue)
        score = 100 - min(variance, 100)

        return round(score)

    @staticmethod
    def get_color_balance(image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        red_mean = np.mean(rgb[:, :, 0])
        green_mean = np.mean(rgb[:, :, 1])
        blue_mean = np.mean(rgb[:, :, 2])

        difference = np.std([red_mean, green_mean, blue_mean])
        score = 100 - min(difference, 100)

        return round(score)

    # ==========================================================
    # MARKETING POSTER METRICS
    # ==========================================================

    @staticmethod
    def get_whitespace(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        white_pixels = np.sum(gray > 240)
        total_pixels = gray.shape[0] * gray.shape[1]

        whitespace = (white_pixels / total_pixels) * 100

        return round(whitespace)

    @staticmethod
    def get_text_density(image):
        """
        Uses Tesseract locally.
        On Render (where Tesseract is unavailable), returns a safe fallback.
        """

        try:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            data = pytesseract.image_to_data(
                rgb,
                output_type=pytesseract.Output.DICT,
            )

            occupied_area = 0
            words = 0

            for i, text in enumerate(data["text"]):
                if text.strip():
                    words += 1
                    occupied_area += (
                        data["width"][i] *
                        data["height"][i]
                    )

            total_area = image.shape[0] * image.shape[1]
            density = (occupied_area / total_area) * 100
            score = max(0, 100 - density)

            return {
                "words_detected": words,
                "density_percentage": round(density, 2),
                "score": round(score),
            }

        except TesseractNotFoundError:
            print("⚠️ Tesseract not available. Skipping text density analysis.")

            return {
                "words_detected": 0,
                "density_percentage": 0,
                "score": 50,
            }

        except Exception as error:
            print(f"Text Density Error: {error}")

            return {
                "words_detected": 0,
                "density_percentage": 0,
                "score": 50,
            }
