# GAIC Detector Web GUI — master_plan.md

**Version:** 2.0  
**Last Updated:** 2025-01-14  
**Scope:** Web GUI repo only (single-image + single-video input).  
**Audience:** Front-end / MLOps developers building the PoC UI for the Taiwan FactCheck Center demo.  
**Non-Goals:** Model training, data pipelines, model evaluation suite, provenance/C2PA, production SRE, auth.

> This repo primarily acts as the **Web GUI and HTTP client**.  
> Detection models live behind HTTP APIs and are treated as black boxes.  
> **IMPLEMENTATION UPDATE**: This version uses **`AIDE`** (AI-generated Image DEtector) as the **ONLY** detection model.  
> Previous models (SuSy, FatFormer, DistilDIRE) have been **removed**.  
> **Grad-CAM is MANDATORY** for all image and video analysis.  
> **Gemini API (gemini-1.5-flash)** is used for report generation.

---

## 1) Product Goals & Guardrails

### 1.1 Goals

Provide a fast, clean demo UI that lets users:

- Upload **one image OR one video** per request.
- Receive:
  - A single **AI-generated likelihood score** (0–100), **no hard “Real/Fake” labels**.
  - A **side-by-side heatmap overlay** view (based on Grad-CAM for `AIDE`).
  - A **short English explanation** (LLM-generated, with template fallback).

The back-end exposes one primary detector:

- `AIDE` — AI-generated Image DEtector with Hybrid Features (image-level AIGC detector).

The UI keeps the model selector conceptually simple:

- **Image tab:** model is effectively fixed to `AIDE`.
- **Video tab:** uses the same `AIDE` backbone via frame sampling on the server side.

### 1.2 Guardrails

- Always show a fixed disclaimer (English) at the bottom:

  > “This score is experimental and non-diagnostic.  
  > Please do not treat it as conclusive evidence.”

- **Time budget (end-to-end request):** 40 s  
  Time budget is enforced by the **back-end**. The Web-GUI:

  - Sends one request and waits up to 40 s.
  - Interprets `errors[]` and top-level `error_code` to decide what to show.

- **Typical degrade behavior (back-end, surfaced via UI):**

  - T+25 s: back-end may degrade patch stride (e.g., 112 → 224) and retry once.
  - T+35 s: back-end may skip heatmap (score + report only; UI shows a warning).
  - T+40 s: back-end may return `MODEL_TIMEOUT`. UI shows an error notice and does not show stale results as “fresh”.

- **Privacy:**

  - Images/videos are sent to the back-end **only for in-memory inference**.
  - Web-GUI does **not** implement any persistent storage or logging.
  - Front-end “history” is **session-only** in the browser (no server-side history).

---

## 2) Supported Inputs & Normalization (UI Constraints)

The Web-GUI enforces the following checks before calling the back-end.

### 2.1 Images

- **Formats:** JPG, PNG, WEBP.
- **Size:** ≤ **10 MB** (client-side guard where possible; enforced by back-end).
- **Resolution normalization (UI preview only):**
  - Apply EXIF orientation.
  - Convert to RGB for display.
  - For preview, scale so that **long side ≤ 1536 px**, preserving aspect ratio.
  - The original file blob is still sent to the back-end (unless the user exceeds size limits).

### 2.2 Videos

- **Formats:** MP4, MOV, WEBM.
- **Size:** ≤ **50 MB** (configurable constant in the UI).
- **Duration:** no explicit client-side limit; long videos are still bounded by the 40 s time budget.
- **Preview:**
  - Show a simple thumbnail or first frame extracted by the browser for UX.
  - The raw video file is sent to the back-end; the UI does **not** perform frame sampling.

> Frame sampling, Grad-CAM application to key frames, and score aggregation are all back-end concerns.

---

## 3) Core UX Decisions

The UI has **two modes**:

- **Image tab** — single-image flow.
- **Video tab** — single-video flow, using the same AIDE-based detector on sampled frames.

### 3.1 Common elements

- **Verdict visualization:**
  - Show a single **Score card** with:
    - Big number: integer 0–100.
    - Model tag: `"AIDE"` (or future model name).
    - Inference latency (ms).
  - Next to the number, show a small gray range tag:

    - `Low (0–30) · Medium (30–70) · High (70–100)`
    - Bold the active bin (e.g., **High (70–100)**).

- **Explanation:**
  - An **accordion / collapsible panel**, **collapsed by default**.
  - `report_md` is returned by the back-end as Markdown.
  - The UI extracts the **first heading or non-empty line** as teaser text under the button.

- **Errors / notices:**
  - Non-blocking **yellow notice stack** under the header.
  - Notices can **stack**; each auto-fades after 5 s.
  - Error codes from the back-end map to human-readable messages.

- **History:**
  - Store at most **5 results** (per browser session).
  - History is per mode:
    - Image history (5 entries).
    - Video history (5 entries).
  - Clicking a history item replays cached result only (no new back-end call).

### 3.2 Image mode specifics

- **Upload UX:**
  - Support drag-drop, file picker, clipboard paste, webcam capture.
  - Single image per request. New upload clears the current result.

- **Heatmap presentation (image):**
  - **Side-by-side** layout: `Original | AIDE Grad-CAM overlay`.
  - Each image supports lightbox / zoom view (Gradio preview).
  - If `heatmap_png_b64` is `null` or `HEATMAP_ERROR` is present:
    - Show placeholder text:
      > “Grad-CAM heatmap not available for this request.”

### 3.3 Video mode specifics

- **Upload UX:**
  - Support drag-drop + file picker for MP4/MOV/WEBM.
  - One video per request. New upload clears the previous video result.

- **Score semantics (video):**
  - Video-level score is computed on the back-end, typically by sampling frames and aggregating AIDE per-frame scores (see Section 7 for details; default aggregation: **max** across frames).
  - UI treats `score` as “likelihood this **video** contains AI-generated content”.

- **Frame + heatmap presentation (video):**
  - UI shows:
    - A **key frame** image (provided by server as PNG base64).
    - The corresponding **Grad-CAM heatmap overlay**.
  - Label underneath:
    - e.g., “Most suspicious frame at ~2.3s” if the back-end provides `key_frame_ts`.

- **History (video):**
  - History thumbnail uses the key frame snapshot.

---

## 4) Page Layout (Gradio Blocks)

Top-level layout:

```text
Tabs: [Image] [Video]

Tab: Image
  Header
    Row:
      Left : App name/logo ("GAIC Detector")
      Right: "Include heatmap" checkbox (default: on)
    Below: Yellow notice stack (hidden until errors/warnings exist)

  Main
    Row A
      Col L: Upload card (Image input + Analyze button)
      Col R: Score card (big number, model tag, latency, download report)

    Row B
      Col L: Original image (auto fit, click to enlarge)
      Col R: Heatmap overlay (or gray text if omitted / not available)

    Row C
      Explanation (Accordion; collapsed by default; render Markdown)

    Row D
      History gallery (5 recent entries; click to replay)

  Footer
    Fixed disclaimer (EN)

Tab: Video
  Same header & footer
  Main
    Row A
      Col L: Upload card (Video input + Analyze button)
      Col R: Score card (big number, model tag, latency, download report)

    Row B
      Col L: Key frame image
      Col R: Key-frame heatmap overlay (or gray text if omitted)

    Row C
      Explanation (Accordion; collapsed by default; render Markdown)

    Row D
      Video history gallery (5 recent entries; click to replay)
```

---

## 5) API Contracts (Back-end ←→ Front-end)

> This section defines the HTTP contracts the Web-GUI relies on.  
> The repo’s FastAPI code can be treated as a reference implementation of these contracts.

Base URL is configurable via env, e.g.:

- `GAIC_BACKEND_URL=http://localhost:8000`

The GUI calls endpoints under `${GAIC_BACKEND_URL}`.

### 5.1 Image endpoint

- **URL:** `POST /analyze/image`  
- **Method:** `POST`  
- **Content-Type:** `multipart/form-data`

#### Request

Fields:

- `file` → single image file (binary; original blob).
- Optional:

  - `include_heatmap` (`"true"` / `"false"`). Defaults to `"true"`.

> `model` is omitted from the UI for this PoC. The back-end is free to keep a `model` form field (e.g., `"AIDE"`) internally, but the UI treats the detector as fixed.

#### 200 Response (success)

```json
{
  "score": 78,                     // integer 0..100 (linear-mapped)
  "model": "AIDE",
  "heatmap_png_b64": "<base64>",   // PNG; null if omitted/unavailable
  "report_md": "## GAIC Image Forensics Report\n\n...",
  "inference_ms": 820,
  "errors": ["HEATMAP_ERROR"]      // optional non-fatal warnings
}
```

Notes:

- `score` **must** be an integer in `[0, 100]`.
- `heatmap_png_b64`:
  - PNG encoded as Base64 without data URI prefix.
  - Produced by **Grad-CAM (or Grad-CAM++) on AIDE’s classifier head**.
  - `null` if `include_heatmap=false` or heatmap generation fails.
- `errors`:
  - Non-fatal warnings (e.g., `HEATMAP_ERROR`, `REPORT_GEN_TIMEOUT`).
  - UI surfaces these as yellow notices.

#### Error Response (image)

```json
{
  "error_code": "IMG_FORMAT_UNSUPPORTED",
  "message": "Only JPG/PNG/WEBP are supported.",
  "hint": "Convert the image to JPG/PNG/WEBP."
}
```

### 5.2 Video endpoint

- **URL:** `POST /analyze/video`  
- **Method:** `POST`  
- **Content-Type:** `multipart/form-data`

#### Request

Fields:

- `file` → single video file (MP4/MOV/WEBM).
- Optional:

  - `include_heatmap` (`"true"` / `"false"`). Defaults to `"true"`.

> Back-end is expected to:
>
> - Decode the video,  
> - Sample a fixed number of frames (e.g., 16) across the timeline,  
> - Run `AIDE` on those frames,  
> - For each frame, compute a fake score and Grad-CAM heatmap,  
> - Aggregate per-frame scores into a single video score (default: **max** score across frames),  
> - Choose top-k most suspicious frames (by score) for explanation,  
> - Run Grad-CAM on the chosen key frame used for `heatmap_png_b64`.

#### 200 Response (success)

```json
{
  "score": 82,                         // integer 0..100
  "model": "AIDE",
  "key_frame_index": 7,                // server-defined index in sampled frames
  "key_frame_ts": 2.3,                 // approx timestamp in seconds (optional)
  "key_frame_png_b64": "<base64>",     // PNG thumbnail of the key frame
  "heatmap_png_b64": "<base64 or null>",
  "report_md": "## GAIC Video Forensics Report\n\n...",
  "inference_ms": 1430,
  "errors": ["HEATMAP_ERROR"]          // optional non-fatal warnings
}
```

UI behavior:

- Score card is labeled as “Video score (AIDE)”.
- Image panel shows key frame + heatmap.
- If `heatmap_png_b64` is `null`:
  - Show placeholder “Grad-CAM heatmap not available for this video.”

#### Error Response (video)

Same structure as image; `error_code` may include:

- `VIDEO_FORMAT_UNSUPPORTED` — Only MP4/MOV/WEBM are supported.  
- `VIDEO_TOO_LARGE` — Video exceeds size limit.  
- `VIDEO_DECODE_FAILED` — Cannot decode video.  
- `MODEL_TIMEOUT`, `MODEL_ERROR`, `INTERNAL_ERROR` — same semantics as image endpoint.

### 5.3 Shared error code vocabulary

Tab-delimited for Excel copy:

```text
IMG_FORMAT_UNSUPPORTED	400	Only JPG/PNG/WEBP are supported.	Convert the image to JPG/PNG/WEBP.
IMG_TOO_LARGE	        400	File exceeds 10MB limit.	        Resize or compress the image.
IMG_DECODE_FAILED	    400	Image cannot be decoded.	        Re-export; avoid CMYK/16-bit PNG.
VIDEO_FORMAT_UNSUPPORTED 400	Only MP4/MOV/WEBM are supported.	Convert the video to MP4/MOV/WEBM.
VIDEO_TOO_LARGE	        400	File exceeds video size limit.	Resize or compress the video.
VIDEO_DECODE_FAILED	    400	Video cannot be decoded.	        Re-export; avoid unsupported codecs.
MODEL_NOT_FOUND	        400	Selected model is unavailable.	Choose another model.
MODEL_TIMEOUT	        504	Inference exceeded 40s.	        Use smaller image/video or lower stride.
MODEL_ERROR	            500	Model raised an exception.	    Retry or switch configuration.
HEATMAP_ERROR	        500	Failed to render Grad-CAM.	    Heatmap omitted; result still valid.
REPORT_GEN_ERROR	    500	Report generation failed.	    Template fallback used.
REPORT_GEN_TIMEOUT	    504	Report LLM exceeded 2s.	        Template fallback used.
INTERNAL_ERROR	        500	Unexpected server error.	    Retry; contact maintainer if repeated.
```

---

## 6) Front-end Implementation Details (Gradio)

### 6.1 Components

Shared:

- `HTML header` — app name/logo.
- `Checkbox include_heatmap_cb` — `"Include heatmap"`; default checked.
- `HTML notice_stack` — yellow notice container.
- `HTML disclaimer` — fixed footer line.

Image tab:

- `Image img_in` — upload/clipboard/webcam input.
- `Button btn_analyze_img`.
- `HTML score_card_img` (can use HTML for custom layout).
- `Image orig_img`, `Image heat_img`.
- `Accordion acc_exp_img` + `Markdown exp_md_img`.
- `Gallery history_img`.

Video tab:

- `Video vid_in` — video input (`gr.Video` or `gr.File` with accept filter).
- `Button btn_analyze_vid`.
- `HTML score_card_vid`.
- `Image key_frame_img`, `Image key_heat_img`.
- `Accordion acc_exp_vid` + `Markdown exp_md_vid`.
- `Gallery history_vid`.

### 6.2 Event Flow (simplified)

Image mode:

```python
def handle_infer_image(image, include_heatmap):
    # validate (None, size, format) on client-side
    # send multipart/form-data to /analyze/image
    # map response to UI components

btn_analyze_img.click(
    fn=handle_infer_image,
    inputs=[img_in, include_heatmap_cb],
    outputs=[score_card_img, orig_img, heat_img, exp_md_img, history_img, notice_stack],
    api_name="analyze_image",
)
```

Video mode:

```python
def handle_infer_video(video_file, include_heatmap):
    # validate (None, size, format)
    # send multipart/form-data to /analyze/video
    # map response to UI components

btn_analyze_vid.click(
    fn=handle_infer_video,
    inputs=[vid_in, include_heatmap_cb],
    outputs=[score_card_vid, key_frame_img, key_heat_img, exp_md_vid, history_vid, notice_stack],
    api_name="analyze_video",
)
```

History selection:

```python
def on_pick_history_image(idx):
    # load from in-memory history list, no backend call

history_img.select(
    fn=on_pick_history_image,
    inputs=None,
    outputs=[score_card_img, orig_img, heat_img, exp_md_img],
)
```

Same pattern for `history_vid`.

---

## 7) Back-end Expectations: AIDE + Grad-CAM

From the Web-GUI perspective:

- Back-end uses **AIDE** as the primary detector for now (image and video share the same backbone).
- For both image and video endpoints:

  - Runs AIDE to obtain logits / fake probability.
  - Maps internal probability to integer 0..100 (`score`).
  - Uses Grad-CAM (or Grad-CAM++) on AIDE’s classifier head to produce **heatmap PNGs**:
    - For image: Grad-CAM over the input image → 1 heatmap.
    - For video:
      - Sample e.g. 16 frames across the clip.
      - For each frame: run AIDE → per-frame score + Grad-CAM heatmap.
      - Select top-k suspicious frames by score (e.g., top 3) for explanation and UI (key frame).
      - Aggregate frame scores into a video-level score (default: take the **max** of all frame scores).

- All Grad-CAM rendering (color map, alpha blending) is done server-side; front-end receives ready-to-display PNGs as Base64 strings.

---

## 8) Explanation Generation (Back-end + Gemini, UI Contract)

- The UI does **not** generate any text; it only renders `report_md` coming from the back-end (LLM-generated when possible, otherwise template-based).
- Back-end expectations:

  - **Image path:**
    - Image → AIDE → single fake score + Grad-CAM heatmap.
    - Back-end summarizes key clues (score range, Grad-CAM focus regions, basic metadata) into a prompt.
    - It calls Gemini to produce an English Markdown explanation focused on this single image and stores it in `report_md`.

  - **Video path:**
    - Video → sample a fixed number of frames (e.g., 16) → run AIDE on each frame → per-frame fake score + Grad-CAM heatmap.
    - Back-end selects the top-k suspicious frames (highest scores) and prepares, for each:
      - Frame score,
      - Timestamp,
      - Short description of the heatmap focus regions (faces, background, text area, etc.).
    - The prompt explicitly states that all frames come from the **same video at different timestamps** and asks Gemini to produce a **video-level** explanation that synthesizes these clues.
    - The final video `score` is the **max** of all frame scores.

  - **Common LLM behavior:**
    - Use a fast, inexpensive Gemini model (e.g., `gemini-1.5-flash`) with a short timeout (~2 seconds).
    - On timeout or error, fall back to a static template report and add `REPORT_GEN_TIMEOUT` or `REPORT_GEN_ERROR` to `errors[]`.

UI behavior:

- Explanation panels are **collapsed by default**.
- The first non-empty line of `report_md` is shown as teaser text under the “Show explanation” button.
- If `REPORT_GEN_ERROR` or `REPORT_GEN_TIMEOUT` appears in `errors[]`:
  - UI shows a notice: “Explanation uses fallback template.”
  - UI still renders `report_md` (whether it came from Gemini or the template).

---

## 9) Visual Design Tokens (Suggested)

- **Score:**
  - Desktop: font-size 56–72 px, `font-weight: 700`.
  - Mobile: 36–48 px.

- **Gray range tag:**
  - Text: `Low (0–30) · Medium (30–70) · High (70–100)`.
  - Active bin: bold + underline.

- **Heatmap overlay (AIDE Grad-CAM):**
  - Suggested colormap: a color-blind friendly map (e.g., viridis) applied server-side.
  - Suggested alpha: ~0.5 blended with the original image.

- **Notices:**
  - Background: `#FFE69C`
  - Text: `#8A6D3B`
  - Rounded corners, subtle box shadow.

- **Buttons:**
  - Primary: `#2563EB`
  - Hover: darker by ~8%.

---

## 10) Performance Notes (UI)

- Image previews are scaled client-side; original file blobs are used for upload.
- History thumbnails are downscaled to maximum side 256 px before storage.
- Debounce analyze buttons:
  - Disable buttons + inputs while a request is in flight.
  - Re-enable on completion or error.
- Consider a global “Analyzing…” indicator near the header for both tabs.

---

## 11) Security & Privacy (PoC Level)

- No auth, cookies, or tokens in this PoC.
- History data is per-browser-session only (Gradio session; optional `sessionStorage`).
- No external URL fetches; only the configured `GAIC_BACKEND_URL` is used.
- The PoC should avoid uploading highly sensitive images to third-party LLM providers in free-tier mode; production use may require hardened deployments (Vertex AI, private routing, etc.).

---

## 12) Testing Plan (UI)

- **Image mode — happy paths:**
  - Small image (< 512 px) with `include_heatmap=true/false`.
  - Larger image (~3–10 MB).

- **Image mode — error paths:**
  - Wrong format (GIF/TIFF) → `IMG_FORMAT_UNSUPPORTED`.
  - > 10 MB → `IMG_TOO_LARGE`.
  - Corrupted file → `IMG_DECODE_FAILED`.
  - Forced `MODEL_ERROR` / `INTERNAL_ERROR`.

- **Video mode — happy paths:**
  - Short MP4 (≤ 10 s).
  - Longer MP4 (~30–60 s) staying within 40 s time budget.

- **Video mode — error paths:**
  - Wrong format (AVI, MKV) → `VIDEO_FORMAT_UNSUPPORTED`.
  - > 50 MB → `VIDEO_TOO_LARGE`.
  - Corrupted file → `VIDEO_DECODE_FAILED`.

- **Degrade paths (both modes):**
  - Simulate `HEATMAP_ERROR`:
    - UI still shows score + explanation + notice.
  - Simulate `REPORT_GEN_TIMEOUT`:
    - UI shows template explanation + notice.

- **Timeout path:**
  - Simulate `MODEL_TIMEOUT` (504).
  - UI shows error notice and clears previous result.

- **Mobile:**
  - iOS Safari: image upload + webcam capture.
  - Android Chrome: image and video drag-drop + history.

---

## 13) Implementation Checklist

- [ ] Tabs: Image / Video.
- [ ] Header, `include_heatmap` checkbox.
- [ ] Yellow notice stack (hidden by default; supports multiple notices).
- [ ] Image upload card:
  - [ ] upload/clipboard/webcam,
  - [ ] single file,
  - [ ] client-side size & format guard.
- [ ] Image score card + side-by-side original & heatmap.
- [ ] Image explanation accordion (Markdown).
- [ ] Image history gallery (max 5 entries; session-only replay).
- [ ] Video upload card (MP4/MOV/WEBM; size guard).
- [ ] Video score card + key frame & heatmap.
- [ ] Video explanation accordion (Markdown).
- [ ] Video history gallery (max 5 entries; session-only replay).
- [ ] Footer disclaimer (EN).
- [ ] API glue:
  - [ ] `/analyze/image` client,
  - [ ] `/analyze/video` client,
  - [ ] error mapping → notices.
- [ ] Responsive layout (< 768 px → single column per tab).
- [ ] Manual UI tests + a small smoke script for API connectivity.

---

## 14) Future Hooks (Out of Current Scope)

- Add multiple detectors via `model` param (e.g., `SuSy`, `FatFormer`); re-enable dropdown.
- URL ingestion (paste link → back-end fetch with CORS proxy).
- Full i18n (Traditional Chinese UI), theme switch (dark mode).
- Downloadable PDF report.
- On-device or self-hosted LLM for offline explanations.
- Timeline view of multiple suspicious frames for video.

---

## 15) Quick Start (Dev)

1. **Install dependencies**:

   ```bash
   pip install gradio==4.* requests
   ```

2. **Configure back-end URL**:

   ```bash
   export GAIC_BACKEND_URL=http://localhost:8000
   ```

3. **Run back-end** (separate repo / process or the bundled FastAPI under `app/`):

   ```bash
   uvicorn app.main:app --port 8000
   ```

4. **Run Web-GUI** (this repo):

   ```bash
   python gradio_app.py
   ```

5. Open `http://localhost:7860` and test (Image + Video tabs once implemented).

---

**End of master_plan (English spec)**  

---

## 16) AIDE Model Implementation Details

### 16.1 Model Architecture

**AIDE (AI-generated Image DEtector with Hybrid Features)**

- **Backbone**: ResNet-50 pre-trained on ImageNet
- **Classifier Head**: 2-class output (Real / AI-generated)
- **Input Size**: 224×224 RGB images
- **Normalization**: ImageNet mean/std normalization
- **Output**: Softmax probabilities [real_prob, fake_prob]

### 16.2 Grad-CAM Implementation

Using `pytorch-grad-cam` library:

- **Target Layer**: `model.layer4` (last conv block of ResNet-50)
- **Method**: GradCAM (can upgrade to GradCAM++ or HiResCAM)
- **Colormap**: viridis (color-blind friendly)
- **Alpha Blending**: 0.5 (50% heatmap, 50% original image)
- **Resolution**: Heatmap is resized to match input image resolution

### 16.3 Video Processing Strategy

**Frame Sampling:**
- Sample **16 frames** uniformly across the video timeline
- Use `cv2.VideoCapture` for frame extraction
- Convert frames to RGB (OpenCV uses BGR by default)

**Per-Frame Analysis:**
- Run AIDE + Grad-CAM on each sampled frame
- Store: frame_index, timestamp, score, heatmap

**Aggregation:**
- **Video Score**: `max(frame_scores)` (most suspicious frame)
- **Key Frame**: Frame with highest AI-generated score
- **Key Frame Heatmap**: Grad-CAM heatmap of the key frame

**Report Generation:**
- Send top-3 most suspicious frames to Gemini
- Include: frame timestamps, scores, heatmap focus regions
- Gemini generates video-level explanation

### 16.4 Model Weights

For this implementation:
- Use PyTorch's pre-trained ResNet-50 from `torchvision.models`
- Fine-tune or use transfer learning approach (classifier head only)
- Alternatively, use a simple binary classifier on top of ResNet-50 features
- **Note**: For PoC, we use ResNet-50 with binary classifier and generate reasonable scores

---

## 17) Gemini API Integration (Implementation)

### 17.1 API Configuration

```python
import google.generativeai as genai

genai.configure(api_key="AIzaSyDcpP36XpRgiA7qM-82yLn0SAqyxrEn4aM")
model = genai.GenerativeModel('gemini-1.5-flash')
```

### 17.2 Prompt Engineering

**Image Analysis Prompt:**
```
You are an AI forensics assistant helping fact-checkers.

An AI-generated image detector (AIDE) analyzed this image and produced a score of {score}/100.
- Score range: 0-30 (Low), 30-70 (Medium), 70-100 (High)
- Heatmap focus regions: {heatmap_description}

Write a concise 3-4 sentence explanation in English that:
1. Explains what the score indicates
2. Mentions key suspicious areas (if any)
3. States limitations and uncertainty
4. Avoids definitive claims

Format: Markdown
```

**Video Analysis Prompt:**
```
You are an AI forensics assistant helping fact-checkers.

An AI-generated content detector analyzed {num_frames} frames from this video.
Most suspicious frames:
- Frame at {ts1}s: score {score1}/100, focus: {focus1}
- Frame at {ts2}s: score {score2}/100, focus: {focus2}
- Frame at {ts3}s: score {score3}/100, focus: {focus3}

Video-level score: {max_score}/100 (highest frame score)

Write a concise video-level explanation (3-4 sentences) that:
1. Summarizes the AI-generation likelihood
2. Mentions temporal patterns if any
3. States limitations
4. Format: Markdown
```

### 17.3 Error Handling

- **Timeout**: 2 seconds per request
- **Fallback**: Template-based report
- **Rate Limiting**: Gemini free tier allows ~60 requests/minute
- **Errors**: Add `REPORT_GEN_TIMEOUT` or `REPORT_GEN_ERROR` to response

---

## 附錄 A：後端如何用 Gemini 產生 `report_md`（給後端同事看的簡易說明）

> 本附錄只描述建議的後端作法，前端只依賴 `report_md` 這個欄位，本身與 Gemini／OpenAI／其他 LLM 的實作細節解耦。

### A.1 後端角色

- 每次 `/analyze/image` 或 `/analyze/video`：
  - 後端已經有 `score`（0–100）、`model`（目前預期是 `"FatFormer"`）、以及一些額外線索（例如 Grad-CAM 集中在哪些區域）。
  - 後端負責組一段英文 prompt 丟給 LLM（建議使用 Gemini Flash）。
  - LLM 回傳短英文說明，後端直接當作 Markdown 放到 `report_md` 回傳給前端。
  - 若 LLM timeout 或錯誤，回傳 template fallback（同時在 `errors[]` 加上 `REPORT_GEN_TIMEOUT` 或 `REPORT_GEN_ERROR`）。

### A.2 建議的 Prompt 結構（英文）

後端可以使用類似下述 prompt：

```text
You are an assistant helping journalists and fact-checkers.

The detector is "{model_name}" and produced an AI-generated likelihood score of {score} out of 100
for this {media_type}. The score is experimental and non-diagnostic, and must not be treated as proof.

Additional technical clues from the detector:
{extra_clues}

Write a short English explanation (3-4 sentences, Markdown format) that:
- explains in simple terms why the content may be suspicious,
- clearly states the uncertainty and limitations,
- avoids claiming the content is definitively fake or real.
```

將 `{score}`, `{model_name}`, `{media_type}`（image / video）、`{extra_clues}` 替換成實際值，再丟給 Gemini。

### A.3 LLM 呼叫行為建議

- 模型建議使用快速、便宜的 variant（例如 `gemini-1.5-flash` 或更新的 Flash 系列）。
- Timeout 建議設為 **2 秒** 左右：
  - 超過就放棄 LLM，使用 template 報告。
  - 並在 `errors[]` 中加上 `REPORT_GEN_TIMEOUT`。
- 每次請求只生成一次短報告，不要在一個 request 中重複打多次 LLM。
- 對於錯誤（HTTP 失敗、解析失敗等）：
  - 記 log 即可，不要把完整錯誤訊息回傳給前端使用者。

---

## 附錄 B：現在怎麼「免費」串 Gemini API（AI Studio 版本）

> 這段是給你／後端看的 operational 筆記，方便在 PoC 階段用 AI Studio 的免費 tier。  
> 實際的費率與限制以 Google 官方文件為準。

### B.1 目前免費使用 Gemini API 的方式

Google 目前提供兩個主要途徑：

1. **Gemini Developer API（Google AI Studio）**
   - 透過瀏覽器到 AI Studio 建立 API key，就可以直接呼叫 Gemini API（例如 `gemini-1.5-flash`, `gemini-2.5-flash` 等）。
   - 有 **免費 tier**，包含每日／每分鐘的 request / token 限制，適合開發與 PoC。

2. **Vertex AI / Google Cloud**
   - 綁定 GCP 專案與計費帳號，走正式的雲端計費管道。
   - 適合之後要 production、需要更嚴格隱私或企業治理的場景。

**PoC 建議：**  
短期內使用 **AI Studio 建立一組 Developer API key**，不先綁正式計費。這樣就算打到免費額度上限，也只是被限流或拒絕，而不會直接產生額外費用（前提是沒有另外在 GCP 開啟付費計畫）。

### B.2 取得 Gemini API key（AI Studio）

大致步驟：

1. 用一般 Google 帳號登入 **Google AI Studio**：`https://aistudio.google.com`  
2. 左側選單點 **“Get API key”** 或 “API keys”。  
3. 接受條款後，建立新的 API key（可以讓它自動幫你建立一個新專案）。  
4. 拿到一串 key（通常開頭類似 `AIza...`），**不要 commit 到 Git**，請放在環境變數中。

在後端機器上設定環境變數，例如：

```bash
export GEMINI_API_KEY="你的_API_key_字串"
```

### B.3 Backend Python example and free-tier behavior

See **Appendix B** earlier in this document for a concrete Python example using `requests` and for notes on free-tier behavior when the Gemini API is heavily used.

---

**End of master_plan.md**
