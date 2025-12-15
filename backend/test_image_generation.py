#!/usr/bin/env python3
"""
圖片生成測試腳本
使用 Gemini 生成提示詞，然後使用 Gemini Imagen API 產生圖片
"""

import os
import sys
import time
from pathlib import Path
from PIL import Image
from io import BytesIO


def test_gemini_prompt():
    """使用 Gemini 生成圖片提示詞"""
    print("=" * 60)
    print("Step 1: Generate Image Prompt with Gemini")
    print("=" * 60)

    max_retries = 2
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            import google.generativeai as genai

            api_key = 'AIzaSyCP6whi1CKXcDcFmDcIh0PgXKwJqhyo1P0'
            if not api_key:
                print("✗ GEMINI_API_KEY not found in environment")
                break

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel('gemini-2.5-flash')

            gift_name = "咖啡杯"
            who_likes = "喜歡咖啡的上班族"
            usage_situation = "早上需要提神的時候"

            prompt = f"""
請為「{gift_name}」這個禮物生成一個適合用於 AI 圖片生成的英文提示詞。

參考資訊：
- 適合對象：{who_likes}
- 使用情境：{usage_situation}

請生成一個詳細的英文圖片描述，包含：
1. 禮物本身的外觀（清晰、具體）
2. 溫馨、節慶的氛圍
3. 精美的包裝或呈現方式
4. 光線和色調

只需要回答英文提示詞，不需要其他解釋。
格式：簡潔明確的英文描述，適合圖片生成 AI 使用。
"""

            print(f"Gift: {gift_name}")
            if attempt > 0:
                print(f"Retry {attempt + 1}/{max_retries}...")
            print("Generating prompt...")

            response = model.generate_content(prompt)
            image_prompt = response.text.strip()

            # 清理提示詞（移除引號等）
            image_prompt = image_prompt.strip('"').strip("'")

            print(f"\n✓ Generated Prompt:")
            print(f"  {image_prompt}")
            print()

            return image_prompt

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "overload" in error_msg.lower() or "Timeout" in error_msg:
                if attempt < max_retries - 1:
                    print(f"⚠ API busy, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
            print(f"✗ Failed to generate prompt: {e}")
            break

    # 使用預設提示詞
    print("\n💡 Using default prompt")
    default_prompt = "A beautiful ceramic coffee mug with festive holiday design, wrapped in elegant red and gold gift paper with silk ribbon, warm cozy atmosphere, soft morning light, professional photography"
    print(f"  {default_prompt}")
    print()
    return default_prompt


def test_gemini_imagen(prompt, output_path="test_output"):
    """使用 Gemini Imagen API 生成圖片"""
    print("=" * 60)
    print("Step 2: Generate Image with Gemini Imagen")
    print("=" * 60)

    try:
        from google import genai
        from google.genai import types

        # 建立輸出目錄
        Path(output_path).mkdir(exist_ok=True)

        # 設定 API Key
        api_key = 'AIzaSyCP6whi1CKXcDcFmDcIh0PgXKwJqhyo1P0'
        if not api_key:
            print("✗ GEMINI_API_KEY not found in environment")
            return None

        client = genai.Client(api_key=api_key)

        print(f"Prompt: {prompt}")
        print("Generating image with Imagen 4.0...")
        print("(This may take 10-30 seconds...)")

        # 使用 Imagen 4.0 生成圖片
        response = client.models.generate_images(
            model='gemini-2.5-flash-image',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,  # 生成 1 張圖片
                aspect_ratio='1:1',  # 正方形
                safety_filter_level='block_low_and_above',
                person_generation='allow_adult'
            )
        )

        # 儲存圖片
        saved_files = []
        for idx, generated_image in enumerate(response.generated_images):
            timestamp = int(time.time())
            filename = f"gift_image_{timestamp}_{idx}.png"
            filepath = os.path.join(output_path, filename)

            # generated_image.image 已經是 PIL Image 物件
            # 直接呼叫 show() 方法儲存
            pil_image = generated_image.image
            pil_image.save(filepath)

            # 獲取檔案大小
            file_size = os.path.getsize(filepath) / 1024  # KB

            print(f"\n✓ Image {idx + 1} generated successfully!")
            print(f"  File: {filepath}")
            print(f"  Size: {file_size:.2f} KB")

            saved_files.append(filepath)

        print()
        return saved_files[0] if saved_files else None

    except ImportError as e:
        print(f"✗ Failed to import google.genai: {e}")
        print("\n💡 Install required package:")
        print("   pip install google-genai pillow")
        return None
    except Exception as e:
        print(f"✗ Failed to generate image: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主測試流程"""
    print("\n")
    print("=" * 60)
    print("  GEMINI IMAGE GENERATION TEST")
    print("=" * 60)
    print()

    # Step 1: 使用 Gemini 生成提示詞
    image_prompt = test_gemini_prompt()

    if not image_prompt:
        print("\n✗ Cannot continue without prompt")
        return

    # Step 2: 使用 Gemini Imagen 生成圖片
    image_path = test_gemini_imagen(image_prompt)

    # 結果總結
    print("=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)

    if image_path:
        print(f"\n✅ Success! Image saved to:")
        print(f"   {os.path.abspath(image_path)}")
        print(f"\n📝 Prompt used:")
        print(f"   {image_prompt}")
        print(f"\n💡 Next steps:")
        print(f"   1. Open the image to verify quality")
        print(f"   2. View image: test_output/gift_image_*.png")
        print(f"   3. Integrate into gemini_service.py if satisfied")
    else:
        print("\n✗ Image generation failed")
        print("\n💡 Troubleshooting:")
        print("   1. Check GEMINI_API_KEY is valid")
        print("   2. Ensure google-genai package is installed")
        print("   3. Check if Imagen API is enabled in your Google Cloud project")
        print("   4. Review error messages above")

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
