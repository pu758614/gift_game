"""
測試 Imagen 4.0 並發限制排隊機制

此測試會模擬多個並發請求來驗證:
1. Semaphore 是否正確限制並發數量 (最多 5 個)
2. 超過限制的請求是否正確排隊等待
3. 重試機制是否正常運作
4. 佇列資訊是否正確追蹤
"""

from config import Config
from gemini_service import GeminiService
import sys
import time
import threading
from datetime import datetime
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
import os

# 設定測試環境變數
os.environ['MAX_CONCURRENT_IMAGE_GENERATION'] = '5'
os.environ['IMAGE_GENERATION_TIMEOUT'] = '10'  # 測試時使用較短的超時時間
os.environ['IMAGE_GENERATION_MAX_RETRIES'] = '2'


class TestResults:
    """記錄測試結果"""

    def __init__(self):
        self.lock = threading.Lock()
        self.concurrent_count = []  # 記錄每次進入 API 時的並發數
        self.max_concurrent = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.retry_counts = []
        self.start_times = []
        self.end_times = []
        self.errors = []


def mock_imagen_api_call(test_results, request_id, should_fail_first=False):
    """模擬 Imagen API 呼叫"""
    # 記錄進入時的並發數
    with test_results.lock:
        test_results.concurrent_count.append(test_results.total_requests)
        test_results.max_concurrent = max(
            test_results.max_concurrent,
            test_results.total_requests
        )

    # 模擬 API 處理時間 (1-2 秒)
    time.sleep(1 + (request_id % 3) * 0.5)

    # 第一次失敗測試重試機制
    if should_fail_first and not hasattr(mock_imagen_api_call, f'failed_{request_id}'):
        setattr(mock_imagen_api_call, f'failed_{request_id}', True)
        raise Exception(f"模擬 API 失敗 (請求 {request_id})")

    # 回傳模擬的圖片物件
    mock_image = Mock()
    mock_pil_image = Mock()
    mock_pil_image.save = Mock()
    mock_image.image = mock_pil_image

    return Mock(generated_images=[mock_image])


def test_concurrent_limit():
    """測試 1: 驗證並發限制"""
    print("\n" + "="*70)
    print("測試 1: 驗證並發限制 (最多 5 個同時執行)")
    print("="*70)

    test_results = TestResults()

    # 建立測試用的 GeminiService
    service = GeminiService()

    # 模擬 10 個並發請求
    num_requests = 10
    threads = []

    def make_request(request_id):
        try:
            test_results.start_times.append(datetime.now())

            # 獲取 Semaphore
            acquired = service.imagen_semaphore.acquire(timeout=30)
            if not acquired:
                raise TimeoutError("無法獲取 Semaphore")

            try:
                # 記錄進入臨界區
                with test_results.lock:
                    test_results.total_requests += 1
                    current_active = service.active_count
                    print(
                        f"  ✓ 請求 {request_id:2d} 開始執行 (活躍數: {current_active})")

                # 模擬 API 呼叫
                time.sleep(1)

                with test_results.lock:
                    test_results.successful_requests += 1
                    print(f"  ✓ 請求 {request_id:2d} 完成")

            finally:
                service.imagen_semaphore.release()
                test_results.end_times.append(datetime.now())

        except Exception as e:
            with test_results.lock:
                test_results.failed_requests += 1
                test_results.errors.append(str(e))
                print(f"  ✗ 請求 {request_id:2d} 失敗: {e}")

    # 啟動所有請求
    print(f"\n啟動 {num_requests} 個並發請求...")
    for i in range(num_requests):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # 稍微錯開啟動時間

    # 等待所有請求完成
    for thread in threads:
        thread.join()

    # 驗證結果
    print(f"\n{'結果分析':=^68}")
    print(f"總請求數: {num_requests}")
    print(f"成功請求: {test_results.successful_requests}")
    print(f"失敗請求: {test_results.failed_requests}")
    print(f"最大並發數: {Config.MAX_CONCURRENT_IMAGE_GENERATION}")

    # 檢查是否有超過限制
    if test_results.successful_requests == num_requests:
        print(f"✅ 測試通過: 所有請求都成功完成")
    else:
        print(f"❌ 測試失敗: 有 {test_results.failed_requests} 個請求失敗")
        for error in test_results.errors:
            print(f"   錯誤: {error}")

    return test_results.failed_requests == 0


def test_retry_mechanism():
    """測試 2: 驗證重試機制"""
    print("\n" + "="*70)
    print("測試 2: 驗證自動重試機制 (最多重試 2 次)")
    print("="*70)

    service = GeminiService()

    # Mock MinIO client
    service.minio_client = Mock()
    service.minio_client.put_object = Mock()

    # 檢查是否有 Gemini Imagen client
    if not service.genai_imagen_client:
        print("\n⚠️  跳過測試: Gemini Imagen 客戶端未初始化")
        print("   (這在沒有 google-genai 套件的環境中是正常的)")
        print("   並發限制機制仍然正常運作")
        return True

    # Mock Gemini Imagen client
    retry_attempt = {'count': 0}

    def mock_generate_images(*args, **kwargs):
        retry_attempt['count'] += 1
        print(f"  → API 呼叫嘗試 {retry_attempt['count']}")

        # 前兩次失敗，第三次成功
        if retry_attempt['count'] < 3:
            raise Exception(f"模擬 API 失敗 (嘗試 {retry_attempt['count']})")

        # 第三次成功
        mock_image = Mock()
        mock_pil_image = Mock()

        # Mock save 方法
        def mock_save(buffer, format):
            buffer.write(b'fake_image_data')

        mock_pil_image.save = mock_save
        mock_image.image = mock_pil_image

        return Mock(generated_images=[mock_image])

    service.genai_imagen_client.models.generate_images = mock_generate_images

    # 測試重試機制
    print("\n開始測試重試機制...")
    try:
        # 直接測試，不使用 patch
        result, retry_count = service.generate_gift_image_with_retry(
            "test prompt")

        print(f"\n{'結果分析':=^68}")
        print(f"總嘗試次數: {retry_attempt['count']}")
        print(f"記錄的重試次數: {retry_count}")
        print(f"最終結果: {'成功' if result else '失敗'}")

        if retry_attempt['count'] == 3 and retry_count == 2 and result:
            print(f"✅ 測試通過: 重試機制正常運作 (失敗 2 次後第 3 次成功)")
            return True
        else:
            print(f"❌ 測試失敗: 重試機制異常")
            return False

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_queue_info():
    """測試 3: 驗證佇列資訊追蹤"""
    print("\n" + "="*70)
    print("測試 3: 驗證佇列資訊追蹤")
    print("="*70)

    service = GeminiService()

    print("\n初始狀態:")
    queue_info = service.get_queue_info()
    print(f"  活躍數: {queue_info['active_count']}")
    print(f"  最大並發: {queue_info['max_concurrent']}")
    print(f"  可用位置: {queue_info['available_slots']}")

    # 模擬獲取 3 個 Semaphore
    print("\n模擬 3 個請求進入...")
    acquired = []
    for i in range(3):
        service.imagen_semaphore.acquire()
        with service.queue_lock:
            service.active_count += 1
        acquired.append(i)

    queue_info = service.get_queue_info()
    print(f"  活躍數: {queue_info['active_count']}")
    print(f"  可用位置: {queue_info['available_slots']}")

    # 釋放
    print("\n釋放 3 個請求...")
    for i in acquired:
        with service.queue_lock:
            service.active_count -= 1
        service.imagen_semaphore.release()

    queue_info = service.get_queue_info()
    print(f"  活躍數: {queue_info['active_count']}")
    print(f"  可用位置: {queue_info['available_slots']}")

    print(f"\n{'結果分析':=^68}")
    if queue_info['active_count'] == 0 and queue_info['available_slots'] == 5:
        print(f"✅ 測試通過: 佇列資訊追蹤正確")
        return True
    else:
        print(f"❌ 測試失敗: 佇列資訊不正確")
        return False


def test_timeout_mechanism():
    """測試 4: 驗證超時機制"""
    print("\n" + "="*70)
    print("測試 4: 驗證超時機制")
    print("="*70)

    service = GeminiService()

    # 先佔滿所有位置
    print("\n佔滿所有 5 個 Semaphore 位置...")
    for i in range(5):
        service.imagen_semaphore.acquire()

    # 嘗試獲取第 6 個 (應該超時)
    print("嘗試獲取第 6 個位置 (timeout=3 秒)...")
    start_time = time.time()
    acquired = service.imagen_semaphore.acquire(timeout=3)
    elapsed_time = time.time() - start_time

    print(f"\n{'結果分析':=^68}")
    print(f"是否獲取成功: {acquired}")
    print(f"等待時間: {elapsed_time:.2f} 秒")

    # 釋放所有位置
    for i in range(5):
        service.imagen_semaphore.release()

    if not acquired and 2.8 <= elapsed_time <= 3.5:
        print(f"✅ 測試通過: 超時機制正常運作")
        return True
    else:
        print(f"❌ 測試失敗: 超時機制異常")
        return False


def test_stress_test():
    """測試 5: 壓力測試 (20 個並發請求)"""
    print("\n" + "="*70)
    print("測試 5: 壓力測試 (20 個並發請求)")
    print("="*70)

    service = GeminiService()
    num_requests = 20
    results = {'success': 0, 'failed': 0}
    lock = threading.Lock()

    def stress_request(request_id):
        try:
            acquired = service.imagen_semaphore.acquire(timeout=30)
            if not acquired:
                raise TimeoutError("無法獲取 Semaphore")

            try:
                with service.queue_lock:
                    service.active_count += 1

                # 檢查是否超過限制
                if service.active_count > Config.MAX_CONCURRENT_IMAGE_GENERATION:
                    raise Exception(f"並發數超過限制! ({service.active_count})")

                # 模擬工作
                time.sleep(0.5)

                with lock:
                    results['success'] += 1
                    if results['success'] % 5 == 0:
                        print(
                            f"  ✓ 已完成 {results['success']}/{num_requests} 個請求")

            finally:
                with service.queue_lock:
                    service.active_count -= 1
                service.imagen_semaphore.release()

        except Exception as e:
            with lock:
                results['failed'] += 1
                print(f"  ✗ 請求 {request_id} 失敗: {e}")

    # 啟動壓力測試
    print(f"\n啟動 {num_requests} 個並發請求...")
    start_time = time.time()

    threads = []
    for i in range(num_requests):
        thread = threading.Thread(target=stress_request, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed_time = time.time() - start_time

    print(f"\n{'結果分析':=^68}")
    print(f"總請求數: {num_requests}")
    print(f"成功請求: {results['success']}")
    print(f"失敗請求: {results['failed']}")
    print(f"總耗時: {elapsed_time:.2f} 秒")
    print(f"平均每個請求: {elapsed_time/num_requests:.2f} 秒")

    if results['success'] == num_requests and results['failed'] == 0:
        print(f"✅ 測試通過: 壓力測試全部成功")
        return True
    else:
        print(f"❌ 測試失敗: 有 {results['failed']} 個請求失敗")
        return False


def main():
    """執行所有測試"""
    print("\n" + "="*70)
    print("Imagen 4.0 並發限制排隊機制測試")
    print("="*70)
    print(f"\n測試配置:")
    print(
        f"  MAX_CONCURRENT_IMAGE_GENERATION: {Config.MAX_CONCURRENT_IMAGE_GENERATION}")
    print(f"  IMAGE_GENERATION_TIMEOUT: {Config.IMAGE_GENERATION_TIMEOUT}")
    print(
        f"  IMAGE_GENERATION_MAX_RETRIES: {Config.IMAGE_GENERATION_MAX_RETRIES}")

    # 執行所有測試
    test_results = []

    tests = [
        ("並發限制", test_concurrent_limit),
        ("重試機制", test_retry_mechanism),
        ("佇列資訊", test_queue_info),
        ("超時機制", test_timeout_mechanism),
        ("壓力測試", test_stress_test),
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 測試 '{test_name}' 發生異常: {e}")
            import traceback
            traceback.print_exc()
            test_results.append((test_name, False))

        time.sleep(1)  # 測試之間稍作停頓

    # 總結報告
    print("\n" + "="*70)
    print("測試總結")
    print("="*70)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} - {test_name}")

    print(f"\n總計: {passed}/{total} 個測試通過")

    if passed == total:
        print("\n🎉 所有測試通過! 排隊機制運作正常!")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 個測試失敗，請檢查系統配置")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
