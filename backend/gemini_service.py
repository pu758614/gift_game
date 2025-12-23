import os
import time
import requests
import threading
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

        # 並發控制：Semaphore 限制同時最多 N 個 Imagen API 請求
        self.imagen_semaphore = threading.Semaphore(
            Config.MAX_CONCURRENT_IMAGE_GENERATION)
        self.active_count = 0
        self.queue_lock = threading.Lock()
        print(
            f"Image generation concurrency limit: {Config.MAX_CONCURRENT_IMAGE_GENERATION}", flush=True)

    def guess_gift(self, appearance, who_likes, usage_time):
        """根據描述猜測禮物"""
        if not self.model:
            raise Exception("Gemini API 未初始化，請設定 GEMINI_API_KEY 環境變數")

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
            error_msg = f"Gemini API 猜測禮物失敗: {str(e)}"
            print(f"✗ {error_msg}", flush=True)
            raise Exception(error_msg)

    def generate_gift_image_prompt(self, gift_name, appearance, who_likes):
        """使用固定模板生成圖片描述提示詞"""
        # 如果是中文禮物名稱，用 AI 快速翻譯成英文
        if self.model and any('\u4e00' <= char <= '\u9fff' for char in gift_name):
            try:
                translate_response = self.model.generate_content(
                    f"請將「{gift_name}」翻譯成英文，只回答英文單詞或短語，不要其他內容。"
                )
                gift_name_en = translate_response.text.strip().strip('"\'')
                print(
                    f"Translated gift name: {gift_name} -> {gift_name_en}", flush=True)
            except Exception as e:
                print(f"Translation failed, using original: {e}", flush=True)
                gift_name_en = gift_name
        else:
            gift_name_en = gift_name

        # 固定模板：包含溫馨節慶氛圍和精美包裝
        prompt = f"A beautiful {gift_name_en}, elegantly wrapped with festive ribbon and gift paper, warm cozy lighting, holiday atmosphere, product photography, high quality, professional"

        print(
            f"Using fixed template for image generation: {prompt}", flush=True)
        return prompt

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

            # 回傳相對路徑 (不含 base URL)
            relative_path = f"/{self.minio_bucket}/{filename}"
            full_url = f"{Config.MINIO_PUBLIC_URL}{relative_path}"

            print(f"✓ Image generated and uploaded successfully!", flush=True)
            print(f"  Full URL: {full_url}", flush=True)
            print(f"  Relative path: {relative_path}", flush=True)
            print(f"  Size: {image_size / 1024:.2f} KB", flush=True)

            return relative_path

        except Exception as e:
            print(f"✗ Failed to upload to MinIO: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return None

    def _generate_with_gemini(self, prompt):
        """使用 Gemini Imagen 4.0 生成圖片並上傳到 MinIO（含並發控制）"""
        if not self.genai_imagen_client:
            print("✗ Gemini Imagen client not initialized", flush=True)
            return None

        if not self.minio_client:
            print("✗ MinIO client not initialized", flush=True)
            return None

        # 使用 Semaphore 控制並發（含 timeout）
        acquired = self.imagen_semaphore.acquire(
            timeout=Config.IMAGE_GENERATION_TIMEOUT)
        if not acquired:
            raise TimeoutError(
                f"等待圖片生成佇列超時 ({Config.IMAGE_GENERATION_TIMEOUT} 秒)")

        try:
            # 更新活躍計數
            with self.queue_lock:
                self.active_count += 1
            print(
                f"🎨 開始生成圖片 (活躍: {self.active_count}/{Config.MAX_CONCURRENT_IMAGE_GENERATION})", flush=True)

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

                    # 回傳相對路徑 (不含 base URL)
                    relative_path = f"/{self.minio_bucket}/{filename}"
                    full_url = f"{Config.MINIO_PUBLIC_URL}{relative_path}"

                    print(f"✓ Image generated and uploaded successfully!", flush=True)
                    print(f"  Full URL: {full_url}", flush=True)
                    print(f"  Relative path: {relative_path}", flush=True)
                    print(f"  Size: {image_size / 1024:.2f} KB", flush=True)

                    return relative_path

                except Exception as e:
                    print(f"✗ Failed to upload to MinIO: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
                    return None

            return None

        except ImportError as e:
            print(f"✗ Failed to import Gemini types: {e}", flush=True)
            return None
        finally:
            # 釋放 Semaphore 並更新計數
            with self.queue_lock:
                self.active_count -= 1
            self.imagen_semaphore.release()
            print(
                f"✓ 圖片生成完成，釋放佇列位置 (活躍: {self.active_count}/{Config.MAX_CONCURRENT_IMAGE_GENERATION})", flush=True)

    def generate_gift_image_with_retry(self, prompt, output_dir=None):
        """生成圖片並自動重試（最多 N 次）"""
        max_retries = Config.IMAGE_GENERATION_MAX_RETRIES
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = attempt * 5  # exponential backoff: 5s, 10s
                    print(f"⏳ 等待 {wait_time} 秒後重試...", flush=True)
                    time.sleep(wait_time)
                    print(f"🔄 重試第 {attempt} 次...", flush=True)

                result = self.generate_gift_image(prompt, output_dir)
                if result:
                    if attempt > 0:
                        print(f"✓ 重試成功！(第 {attempt} 次)", flush=True)
                    return result, attempt  # 回傳結果與重試次數
                else:
                    raise Exception("圖片生成回傳 None")

            except Exception as e:
                last_error = e
                print(
                    f"✗ 圖片生成失敗 (嘗試 {attempt + 1}/{max_retries + 1}): {str(e)}", flush=True)
                if attempt >= max_retries:
                    print(f"✗ 已達最大重試次數 ({max_retries} 次)，放棄重試", flush=True)
                    raise Exception(
                        f"圖片生成失敗 (已重試 {max_retries} 次): {str(last_error)}")

        raise Exception(f"圖片生成失敗: {str(last_error)}")

    def get_queue_info(self):
        """取得目前佇列資訊"""
        with self.queue_lock:
            return {
                'active_count': self.active_count,
                'max_concurrent': Config.MAX_CONCURRENT_IMAGE_GENERATION,
                'available_slots': Config.MAX_CONCURRENT_IMAGE_GENERATION - self.active_count
            }


# 創建全局服務實例
gemini_service = GeminiService()
