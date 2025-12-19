/**
 * 生成瀏覽器指紋
 * 結合多種瀏覽器特徵來創建唯一標識
 */

export const generateFingerprint = async () => {
  const components = [];

  // 1. User Agent
  components.push(navigator.userAgent);

  // 2. 螢幕解析度
  components.push(`${screen.width}x${screen.height}x${screen.colorDepth}`);

  // 3. 時區
  components.push(Intl.DateTimeFormat().resolvedOptions().timeZone);

  // 4. 語言
  components.push(navigator.language);

  // 5. 平台
  components.push(navigator.platform);

  // 6. CPU 核心數
  components.push(navigator.hardwareConcurrency);

  // 7. Canvas 指紋
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const text = 'gift-game-fingerprint';
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText(text, 2, 2);
    components.push(canvas.toDataURL());
  } catch (e) {
    components.push('canvas-error');
  }

  // 8. WebGL 指紋
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (gl) {
      const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
      if (debugInfo) {
        components.push(gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL));
        components.push(gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL));
      }
    }
  } catch (e) {
    components.push('webgl-error');
  }

  // 9. 觸控支援
  components.push(navigator.maxTouchPoints || 0);

  // 10. Cookie 啟用
  components.push(navigator.cookieEnabled);

  // 11. LocalStorage 支援
  try {
    localStorage.setItem('test', 'test');
    localStorage.removeItem('test');
    components.push(true);
  } catch (e) {
    components.push(false);
  }

  // 合併所有特徵並生成 hash
  const fingerprint = await hashString(components.join('|||'));

  return fingerprint;
};

/**
 * 使用 SubtleCrypto API 生成 SHA-256 hash
 */
const hashString = async (str) => {
  const encoder = new TextEncoder();
  const data = encoder.encode(str);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
};

/**
 * 獲取或生成指紋（帶快取）
 */
export const getFingerprint = async () => {
  // 先檢查 localStorage 是否有快取
  const cached = localStorage.getItem('voter_fingerprint');
  if (cached) {
    return cached;
  }

  // 生成新指紋
  const fingerprint = await generateFingerprint();

  // 快取到 localStorage
  localStorage.setItem('voter_fingerprint', fingerprint);

  return fingerprint;
};
