"""Report generation with Gemini LLM and template fallback."""

import asyncio
from typing import Optional, Tuple, List, Dict

from app.config import (
    GEMINI_ENABLED,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TIMEOUT,
    MODEL_NAME
)


def generate_template_report(score: int, model: str, media_type: str = "image") -> str:
    """
    Generate template-based report.
    
    Args:
        score: Integer score 0-100
        model: Model name
        media_type: "image" or "video"
        
    Returns:
        Markdown formatted report
    """
    # Determine range
    if score <= 30:
        range_label = "Low"
        interpretation = "shows low likelihood of AI generation"
    elif score <= 70:
        range_label = "Medium"
        interpretation = "shows moderate indicators of potential AI generation"
    else:
        range_label = "High"
        interpretation = "shows strong indicators consistent with AI generation"
    
    media_specific = "image" if media_type == "image" else "video"
    
    report = f"""## GAIC {media_type.title()} 偵測報告

**模型：** {model}  
**分數：** {score}/100 ({range_label} 區間)

### 摘要

這份{media_specific} {interpretation}。分數來自 **{model}** 檢測器，並輔以 Grad-CAM 熱力圖進行解釋。

### 區間解讀

- **Low (0-30)：** 可能為真實或僅少量處理
- **Medium (30-70)：** 可能有 AI 元素或重度編修
- **High (70-100)：** 有明顯 AI 生成跡象

### 注意事項

⚠️ **此評分具實驗性，不能作為最終定論。** 結果可能受下列因素影響：
- {media_specific.title()} 壓縮、重存
- 後製與編修
- 來源與品質
- 模型限制與偏差

### 建議

1. 搭配多種檢測方法
2. 必要時諮詢取證專家
3. 檢查 {media_specific} 的中繼資料與來源脈絡
4. 綜合情境後再做判斷

---

*報告由 GAIC Detector v2.0 產生 | Taiwan FactCheck Center Demo*
"""
    
    return report


async def generate_gemini_report(
    score: int,
    model: str,
    media_type: str = "image",
    extra_context: Optional[Dict] = None
) -> Optional[str]:
    """
    Generate Gemini-based report with timeout.
    
    Args:
        score: Integer score 0-100
        model: Model name
        media_type: "image" or "video"
        extra_context: Optional dict with additional context (for video: frame info)
        
    Returns:
        Markdown report or None if timeout/error
    """
    if not GEMINI_ENABLED or not GEMINI_API_KEY:
        return None
    
    try:
        # Use REST API directly instead of SDK to avoid compatibility issues
        import aiohttp

        # v1beta endpoint works with gemini-2.5-flash for text
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

        # Collect optional context
        inference_ms = None
        orig_size = None

        if extra_context:
            inference_ms = extra_context.get("inference_ms")
            orig_size = extra_context.get("orig_size")

        # Human-friendly strings
        if isinstance(orig_size, (list, tuple)) and len(orig_size) == 2:
            size_str = f"{orig_size[0]}x{orig_size[1]}"
        else:
            size_str = "未提供"
        t_str = f"約 {inference_ms} ms" if inference_ms is not None else "未提供"

        # Build prompt in zh-TW (text-only; image not attached to avoid MAX_TOKENS)
        if media_type == "video" and extra_context and "frames" in extra_context:
            frames_info = extra_context["frames"]
            frames_desc = "\n".join([
                f"- 影格 {idx+1} @ {f['timestamp']:.1f}s：分數 {f['score']}/100"
                for idx, f in enumerate(frames_info[:3])
            ])
            prompt = (
                "用繁體中文、Markdown 簡短輸出。\n"
                f"影片分數：{score}/100，模型：{model}，解析度：{size_str}，推論時間：{t_str}\n"
                f"可疑影格摘要：\n{frames_desc}\n"
                "請輸出：\n"
                "- 觀察(2句)：描述可疑區域位置與疑點。\n"
                "- 限制(1句)：不確定性。\n"
                "- 建議(1句)：後續查核。\n"
            )
        else:
            likelihood = (
                "低度 AI 生成可能" if score <= 30 else
                "中度 AI 生成可能" if score <= 70 else
                "高度 AI 生成可能"
            )
            prompt = (
                "用繁體中文、Markdown 簡短輸出。\n"
                f"影像分數：{score}/100（{likelihood}），模型：{model}，解析度：{size_str}，推論時間：{t_str}\n"
                "請輸出：\n"
                "- 觀察(2句)：描述可疑區域位置與疑點。\n"
                "- 限制(1句)：不確定性或品質限制。\n"
                "- 建議(1句)：後續查核。\n"
            )

        # Text-only parts to keep token usage low and avoid MAX_TOKENS
        parts = [{"text": prompt}]

        async def generate():
            payload = {
                "contents": [{"parts": parts}]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=GEMINI_TIMEOUT)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"Gemini API error {resp.status}: {error_text}")

                    data = await resp.json()

                    # Robust extraction of text from response
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise Exception(f"Gemini response missing candidates: {data}")

                    content = candidates[0].get("content")
                    if isinstance(content, dict):
                        parts_resp = content.get("parts") or []
                    elif isinstance(content, list):
                        parts_resp = content
                    else:
                        parts_resp = []

                    text_chunks = []
                    for p in parts_resp:
                        if isinstance(p, dict) and "text" in p:
                            text_chunks.append(p.get("text", ""))
                        elif isinstance(p, str):
                            text_chunks.append(p)

                    result_text = "".join(text_chunks).strip()
                    if not result_text:
                        raise Exception(f"Gemini response has no text parts: {data}")
                    return result_text

        result = await asyncio.wait_for(generate(), timeout=GEMINI_TIMEOUT)
        return result
        
    except asyncio.TimeoutError:
        print("Gemini generation timeout")
        return None
    except Exception as e:
        print(f"Gemini generation error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def generate_report(
    score: int,
    model: str,
    media_type: str = "image",
    extra_context: Optional[Dict] = None
) -> Tuple[str, Optional[str]]:
    """
    Generate report with Gemini attempt and template fallback.
    
    Args:
        score: Integer score 0-100
        model: Model name
        media_type: "image" or "video"
        extra_context: Optional dict with additional context
        
    Returns:
        Tuple of (report_markdown, error_code or None)
    """
    error = None
    
    # Try Gemini first
    gemini_report = await generate_gemini_report(score, model, media_type, extra_context)
    
    if gemini_report:
        return gemini_report, None
    
    # Fallback to template
    if GEMINI_ENABLED:
        error = "REPORT_GEN_ERROR"
    
    template_report = generate_template_report(score, model, media_type)
    return template_report, error
