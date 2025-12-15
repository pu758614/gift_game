import os
import time
import requests
from pathlib import Path
import google.generativeai as genai
from openai import OpenAI
from config import Config


class GeminiService:
    """AI 服務類（Gemini 用於文字，OpenAI 用於圖片）"""

    def __init__(self):
        """初始化 AI APIs"""
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
        print(f"OpenAI API Key: {openai_key}", flush=True)
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

    def generate_gift_image(self, prompt, output_dir="uploads"):
        """使用選定的引擎生成圖片"""
        try:
            # 建立輸出目錄
            Path(output_dir).mkdir(exist_ok=True)

            print(f"Image generation engine: {self.image_engine}")

            if self.image_engine == 'gemini':
                return self._generate_with_gemini(prompt, output_dir)
            else:  # 預設使用 openai
                return self._generate_with_openai(prompt, output_dir)

        except Exception as e:
            print(f"✗ Failed to generate image: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_with_openai(self, prompt, output_dir):
        """使用 OpenAI DALL-E 3 生成圖片"""
        if not self.openai_client:
            print("✗ OpenAI client not initialized")
            return None

        print(f"Generating image with DALL-E 3...")
        print(f"Prompt: {prompt}")

        # 使用 DALL-E 3 生成圖片
        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )

        # 獲取圖片 URL
        image_url = response.data[0].url
        print(f"Image URL: {image_url}")

        # 下載圖片
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            print(f"✗ Failed to download image: {image_response.status_code}")
            return None

        # 儲存圖片
        timestamp = int(time.time())
        filename = f"gift_image_{timestamp}_0.png"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(image_response.content)

        # 獲取檔案大小
        file_size = os.path.getsize(filepath) / 1024  # KB

        print(f"✓ Image generated successfully with OpenAI!")
        print(f"  File: {filepath}")
        print(f"  Size: {file_size:.2f} KB")

        return filename

    def _generate_with_gemini(self, prompt, output_dir):
        """使用 Gemini Imagen 4.0 生成圖片"""
        if not self.genai_imagen_client:
            print("✗ Gemini Imagen client not initialized")
            return None

        print(f"Generating image with Gemini Imagen 4.0...")
        print(f"Prompt: {prompt}")

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

            # 儲存圖片
            for idx, generated_image in enumerate(response.generated_images):
                timestamp = int(time.time())
                filename = f"gift_image_{timestamp}_{idx}.png"
                filepath = os.path.join(output_dir, filename)

                # generated_image.image 是 PIL Image 物件
                pil_image = generated_image.image
                pil_image.save(filepath)

                # 獲取檔案大小
                file_size = os.path.getsize(filepath) / 1024  # KB

                print(f"✓ Image generated successfully with Gemini!")
                print(f"  File: {filepath}")
                print(f"  Size: {file_size:.2f} KB")

                return filename

            return None

        except ImportError as e:
            print(f"✗ Failed to import Gemini types: {e}")
            return None


# 創建全局服務實例
gemini_service = GeminiService()
