import os
import time
import requests
from io import BytesIO
from pathlib import Path
import google.generativeai as genai
from openai import OpenAI
from minio import Minio
from config import Config


class GeminiService:
    """AI 服務類（Gemini 用於文字，OpenAI 用於圖片，MinIO 用於儲存）"""

    def __init__(self):
        """初始化 AI APIs 和 MinIO"""
        # Gemini 用於文字生成
        gemini_key = Config.GEMINI_API_KEY
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

        # 圖片生成引擎設定
        self.image_engine = Config.IMAGE_GENERATION_ENGINE

        # OpenAI 客戶端
        openai_key = Config.OPENAI_API_KEY
        if openai_key:
            os.environ['OPENAI_API_KEY'] = openai_key
            self.openai_client = OpenAI()
        else:
            self.openai_client = None

        # Gemini Imagen 客戶端
        if gemini_key:
            try:
                from google import genai as genai_client
                self.genai_imagen_client = genai_client.Client(
                    api_key=gemini_key)
            except ImportError:
                print("Warning: google-genai not installed, Gemini Imagen unavailable")
                self.genai_imagen_client = None
        else:
            self.genai_imagen_client = None

        # MinIO 客戶端
        try:
            self.minio_client = Minio(
                Config.MINIO_ENDPOINT,
                access_key=Config.MINIO_ACCESS_KEY,
                secret_key=Config.MINIO_SECRET_KEY,
                secure=Config.MINIO_USE_SSL
            )
            self.minio_bucket = Config.MINIO_BUCKET
            print(
                f"MinIO client initialized: {Config.MINIO_ENDPOINT}/{self.minio_bucket}", flush=True)

            # 確認 bucket 存在
            if not self.minio_client.bucket_exists(self.minio_bucket):
                print(
                    f"Warning: Bucket {self.minio_bucket} does not exist", flush=True)
        except Exception as e:
            print(f"Error initializing MinIO: {e}", flush=True)
            self.minio_client = None

    def guess_gift(self, appearance, who_likes, usage_time):
        """根據描述猜測禮物"""
        if not self.model:
            return "請設定 GEMINI_API_KEY"

        prompt = f"""
        請根據以下線索猜測這是什麼禮物，只需要回答禮物名稱（中文，不超過10個字）：

        1. 這個禮物的外型或材質：{appearance}
        2. 這個禮物通常是什麼人會喜歡的：{who_likes}
        3. 這個禮物通常是在什麼時候使用：{usage_time}

        請直接回答禮物名稱，例如：「咖啡杯」、「藍牙耳機」、「香氛蠟燭」等。
        """

        try:
            response = self.model.generate_content(prompt)
            guess = response.text.strip()
            return guess
        except Exception as e:
            print(f"Gemini API 錯誤: {str(e)}")
            return "神秘禮物"

    def generate_gift_image_prompt(self, gift_name, appearance, who_likes):
        """生成圖片描述提示詞"""
        if not self.model:
            return f"A beautifully wrapped gift box with {gift_name}"

        prompt = f"""
        請為「{gift_name}」這個禮物生成一個適合用於 AI 圖片生成的英文提示詞。

        參考資訊：
        - 外型或材質：{appearance}
        - 適合對象：{who_likes}

        請生成一個詳細的英文圖片描述，包含：
        1. 禮物本身的外觀和材質
        2. 溫馨、節慶的氛圍
        3. 精美的包裝或呈現方式

        只需要回答英文提示詞，不需要其他解釋。格式範例：
        "A beautiful coffee mug with festive design, wrapped in elegant gift paper with a red ribbon, warm lighting, cozy atmosphere"
        """

        try:
            response = self.model.generate_content(prompt)
            prompt_text = response.text.strip()
            return prompt_text
        except Exception as e:
            print(f"生成圖片提示詞錯誤: {str(e)}")
            return f"A beautiful {gift_name} with festive wrapping and warm lighting"

    def generate_gift_image(self, prompt, output_dir=None):
        """使用選定的引擎生成圖片並上傳到 MinIO"""
        try:
            print(f"Image generation engine: {self.image_engine}", flush=True)

            if self.image_engine == 'gemini':
                return self._generate_with_gemini(prompt)
            else:  # 預設使用 openai
                return self._generate_with_openai(prompt)

        except Exception as e:
            print(f"✗ Failed to generate image: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return None

    def _generate_with_openai(self, prompt):
        """使用 OpenAI DALL-E 生成圖片並上傳到 MinIO"""
        if not self.openai_client:
            print("✗ OpenAI client not initialized", flush=True)
            return None

        if not self.minio_client:
            print("✗ MinIO client not initialized", flush=True)
            return None

        print(f"Generating image with gpt-image-1-mini...", flush=True)
        print(f"Prompt: {prompt}", flush=True)

        # 使用 gpt-image-1-mini 生成圖片 (預設回傳 base64)
        response = self.openai_client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            size="1024x1024",
            n=1
        )

        # 檢查 MINIO_PUBLIC_URL
        if not Config.MINIO_PUBLIC_URL:
            print("✗ MINIO_PUBLIC_URL is not configured", flush=True)
            return None

        # 獲取 base64 圖片數據 (gpt-image-1-mini 預設回傳格式)
        import base64
        b64_data = response.data[0].b64_json
        if not b64_data:
            print("✗ No image data returned", flush=True)
            return None

        print(f"✓ Image generated, decoding base64...", flush=True)

        # 解碼 base64 到記憶體
        image_bytes = base64.b64decode(b64_data)
        image_data = BytesIO(image_bytes)
        image_size = len(image_bytes)

        timestamp = int(time.time())
        filename = f"gift_image_{timestamp}_0.png"

        # 上傳到 MinIO
        try:
            self.minio_client.put_object(
                self.minio_bucket,
                filename,
                image_data,
                length=image_size,
                content_type='image/png'
            )

            # 回傳完整 URL
            minio_url = f"{Config.MINIO_PUBLIC_URL}/{self.minio_bucket}/{filename}"

            print(f"✓ Image generated and uploaded successfully!", flush=True)
            print(f"  URL: {minio_url}", flush=True)
            print(f"  Size: {image_size / 1024:.2f} KB", flush=True)

            return minio_url

        except Exception as e:
            print(f"✗ Failed to upload to MinIO: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return None

    def _generate_with_gemini(self, prompt):
        """使用 Gemini Imagen 4.0 生成圖片並上傳到 MinIO"""
        if not self.genai_imagen_client:
            print("✗ Gemini Imagen client not initialized", flush=True)
            return None

        if not self.minio_client:
            print("✗ MinIO client not initialized", flush=True)
            return None

        try:
            from google.genai import types

            # 使用 Imagen 4.0 生成圖片
            response = self.genai_imagen_client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio='1:1',
                    safety_filter_level='block_low_and_above',
                    person_generation='allow_adult'
                )
            )

            # 上傳到 MinIO
            for idx, generated_image in enumerate(response.generated_images):
                timestamp = int(time.time())
                filename = f"gift_image_{timestamp}_{idx}.png"

                # generated_image.image 是 PIL Image 物件，轉為 BytesIO
                pil_image = generated_image.image
                image_buffer = BytesIO()
                pil_image.save(image_buffer, format='PNG')
                image_buffer.seek(0)
                image_size = image_buffer.getbuffer().nbytes

                # 上傳到 MinIO
                try:
                    self.minio_client.put_object(
                        self.minio_bucket,
                        filename,
                        image_buffer,
                        length=image_size,
                        content_type='image/png'
                    )

                    # 回傳完整 URL
                    minio_url = f"{Config.MINIO_PUBLIC_URL}/{self.minio_bucket}/{filename}"

                    print(f"✓ Image generated and uploaded successfully!", flush=True)
                    print(f"  URL: {minio_url}", flush=True)
                    print(f"  Size: {image_size / 1024:.2f} KB", flush=True)

                    return minio_url

                except Exception as e:
                    print(f"✗ Failed to upload to MinIO: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
                    return None

            return None

        except ImportError as e:
            print(f"✗ Failed to import Gemini types: {e}", flush=True)
            return None


# 創建全局服務實例
gemini_service = GeminiService()
