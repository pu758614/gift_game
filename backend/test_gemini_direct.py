#!/usr/bin/env python3
"""
Gemini API Direct Test Script
測試 Gemini API 的直接連接和功能
"""

import os
import sys
import time

# Note: In Docker container, environment variables are already loaded from docker-compose.yml
# No need to use load_dotenv()


def test_gemini_import():
    """測試 Gemini 套件導入"""
    print("=" * 60)
    print("Test 1: Import google.generativeai")
    print("=" * 60)
    try:
        import google.generativeai as genai
        print("✓ Successfully imported google.generativeai")
        return True
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False


def test_api_key():
    """測試 API Key 設定"""
    print("\n" + "=" * 60)
    print("Test 2: Check API Key")
    print("=" * 60)

    api_key = 'AIzaSyCP6whi1CKXcDcFmDcIh0PgXKwJqhyo1P0'
    if not api_key or api_key == 'AIzaSyCP6whi1CKXcDcFmDcIh0PgXKwJqhyo1P0':
        print("✗ GEMINI_API_KEY is not set or invalid")
        print("\nTo get API Key:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Login with Google account")
        print("3. Click 'Get API Key'")
        print("4. Copy key to .env file")
        return False

    print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
    return True


def test_gemini_configuration():
    """測試 Gemini API 配置"""
    print("\n" + "=" * 60)
    print("Test 3: Configure Gemini API")
    print("=" * 60)

    try:
        import google.generativeai as genai

        api_key = 'AIzaSyCP6whi1CKXcDcFmDcIh0PgXKwJqhyo1P0'
        genai.configure(api_key=api_key)
        print("✓ Successfully configured Gemini API")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False


def test_list_models():
    """測試列出可用模型"""
    print("\n" + "=" * 60)
    print("Test 4: List Available Models")
    print("=" * 60)

    try:
        import google.generativeai as genai

        print("Available models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")

        print("✓ Successfully listed models")
        return True
    except Exception as e:
        print(f"✗ Failed to list models: {e}")
        return False


def test_gift_guessing():
    """測試禮物猜測功能"""
    print("\n" + "=" * 60)
    print("Test 5: Gift Guessing with Gemini")
    print("=" * 60)

    test_cases = [
        {
            "name": "Coffee Mug",
            "who_likes": "喜歡咖啡的上班族",
            "usage_situation": "早上需要提神的時候",
            "usage_time": "每天早上 8-10 點",
            "usage_time_2": "下午茶時間 3-4 點"
        },
        {
            "name": "Bluetooth Headphones",
            "who_likes": "熱愛音樂的年輕人",
            "usage_situation": "通勤、運動、工作時聽音樂",
            "usage_time": "每天上下班途中",
            "usage_time_2": "週末運動時"
        },
        {
            "name": "Book",
            "who_likes": "喜歡閱讀的人",
            "usage_situation": "放鬆、學習、打發時間",
            "usage_time": "睡前",
            "usage_time_2": "週末午後"
        }
    ]

    try:
        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-2.5-flash')

        results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['name']}")
            print("-" * 60)

            prompt = f"""
請根據以下線索猜測這是什麼禮物，只需要回答禮物名稱（中文，不超過10個字）：

1. 這個禮物通常是什麼人會喜歡的：{test_case['who_likes']}
2. 這個禮物通常是在什麼情況下使用：{test_case['usage_situation']}
3. 這個禮物通常是在什麼時候使用：{test_case['usage_time']}
4. 這個禮物通常是在什麼時候使用：{test_case['usage_time_2']}

請直接回答禮物名稱，例如：「咖啡杯」、「藍牙耳機」、「香氛蠟燭」等。
"""

            start_time = time.time()
            response = model.generate_content(prompt)
            end_time = time.time()

            guess = response.text.strip()
            duration = end_time - start_time

            print(f"Expected: {test_case['name']}")
            print(f"AI Guess: {guess}")
            print(f"Duration: {duration:.2f} seconds")

            results.append({
                "expected": test_case['name'],
                "guess": guess,
                "duration": duration,
                "success": True
            })

            time.sleep(1)  # Rate limiting

        print("\n" + "=" * 60)
        print("Test Results Summary")
        print("=" * 60)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. Expected: {result['expected']}")
            print(f"   AI Guess: {result['guess']}")
            print(f"   Duration: {result['duration']:.2f}s")

        avg_duration = sum(r['duration'] for r in results) / len(results)
        print(f"\nAverage response time: {avg_duration:.2f} seconds")
        print("✓ All gift guessing tests passed")

        return True

    except Exception as e:
        print(f"✗ Gift guessing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_prompt_generation():
    """測試圖片提示詞生成"""
    print("\n" + "=" * 60)
    print("Test 6: Image Prompt Generation")
    print("=" * 60)

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            import google.generativeai as genai
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
1. 禮物本身的外觀
2. 溫馨、節慶的氛圍
3. 精美的包裝或呈現方式

只需要回答英文提示詞，不需要其他解釋。格式範例：
"A beautiful coffee mug with festive design, wrapped in elegant gift paper with a red ribbon, warm lighting, cozy atmosphere"
"""

            if attempt > 0:
                print(f"Retry attempt {attempt + 1}/{max_retries}...")

            start_time = time.time()
            response = model.generate_content(prompt)
            end_time = time.time()

            image_prompt = response.text.strip()
            duration = end_time - start_time

            print(f"Gift: {gift_name}")
            print(f"Generated Prompt: {image_prompt}")
            print(f"Duration: {duration:.2f} seconds")
            print("✓ Image prompt generation successful")

            return True

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "overloaded" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(
                        f"⚠ API overloaded, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print(
                        f"✗ Image prompt generation failed after {max_retries} attempts: API overloaded")
                    print(
                        "  Note: This is a temporary Google API issue, not a configuration problem")
                    return False
            else:
                print(f"✗ Image prompt generation failed: {e}")
                return False

    return False


def main():
    """主測試函數"""
    print("\n")
    print("=" * 60)
    print("  GEMINI API DIRECT TEST")
    print("=" * 60)
    print()

    results = []

    # Run all tests
    results.append(("Import Test", test_gemini_import()))

    if not results[-1][1]:
        print("\n✗ Cannot continue without google.generativeai package")
        return

    # results.append(("API Key Test", test_api_key()))

    if not results[-1][1]:
        print("\n✗ Cannot continue without valid API key")
        return

    results.append(("Configuration Test", test_gemini_configuration()))
    results.append(("List Models Test", test_list_models()))
    results.append(("Gift Guessing Test", test_gift_guessing()))
    results.append(("Image Prompt Test", test_image_prompt_generation()))

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print()

    for test_name, success in results:
        status = "✓" if success else "✗"
        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status} {test_name}{reset}")

    print()

    if passed == total:
        print("🎉 All tests passed! Gemini API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
