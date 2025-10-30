# GAIC Detector Web GUI — master_plan.md

**Version:** 1.1
**Scope:** Web GUI only (image input).
**Audience:** Developers building the PoC UI for Taiwan FactCheck Center demo.
**Non‑Goals:** Training/data pipelines, model eval suite, provenance/C2PA, production SRE.

---

## 1) Product Goals & Guardrails

**Goal:** Provide a fast, clean demo UI that lets users upload one image and receive:

* A single **AI‑generated likelihood score** (0–100), **no hard labels**.
* A **side‑by‑side heatmap** overlay view.
* A **short English explanation** (LLM‑generated, template fallback).
* Ability to switch among **three detectors**: `SuSy` (default), `FatFormer`, `DistilDIRE`.

**Guardrails:**

* Show fixed disclaimer (English): *“This score is experimental and non‑diagnostic.”*
* **Time budget:** total 40 s/request.

  * T+25 s: degrade patch stride (112 → 224) and retry once.
  * T+35 s: skip heatmap (return score + report; add warning).
  * T+40 s: timeout error.
* **Privacy:** process in memory; do not persist images server‑side. Front‑end history is client‑side only.

---

## 2) Supported Inputs & Normalization

* **Formats:** JPG, PNG, WEBP (single image).
* **Size:** ≤ 10 MB.
* **Resolution:** auto EXIF rotation → RGB → **long side 1536 px** (preserve aspect).
* **Patch policy (for patch‑based models):** 224×224 window; **stride 112** (degrade to 224 when needed).

---

## 3) Core UX Decisions

* **Verdict visualization:** single **Score card** only (0–100). Next to the number, display subtle gray range tag: `Low (0–30) · Medium (30–70) · High (70–100)` with the active bin bolded.
* **Heatmap presentation:** **side‑by‑side** (Original | Overlay). Add **lightbox** to view each pane at full size.
* **Model selector:** **global, top‑fixed** dropdown.
* **Explanation:** **collapsed by default** (button: *Show explanation*). LLM on, 2 s timeout; fallback to template.
* **Errors:** non‑blocking **yellow notice bar**; stackable; auto fade after 5 s.
* **Upload:** drag‑drop + clipboard paste + webcam capture (mobile).
* **URL intake:** disabled (out of scope for now).
* **Mobile layout:** single column (Score → Images → Explanation → History).
* **History:** keep last 5 results **in front‑end session** (thumbnails <= 256 px). Click to **replay** (no re‑compute).
* **Language:** English‑only UI for now.

---

## 4) Page Layout (Gradio Blocks)

```
Header
  Left: App name/logo
  Right: Model dropdown + "Include heatmap" checkbox (default: on)
  Below: Yellow notice stack (hidden until errors)

Main
  Row A
    Col L: Upload card (Image component)
    Col R: Score card (big number, model tag, latency, download report)

  Row B
    Col L: Original image (auto fit)
    Col R: Heatmap overlay (or gray text if omitted)

  Row C
    Explanation (Accordion; collapsed by default; Markdown content)

  Row D
    History gallery (5 recent; click to replay)

Footer
  Fixed disclaimer in English
```

---

## 5) API Contract (Back‑end → Front‑end)

**Endpoint:** `POST /analyze/image`

**Request (multipart/form-data):**

* `file` → single image file
* Optional params: `model` in {`SuSy`, `FatFormer`, `DistilDIRE`}; `include_heatmap` (bool; default true)

**200 Response:**

```json
{
  "score": 78,                // integer 0..100 (linear-mapped)
  "model": "SuSy",
  "heatmap_png_b64": "<base64 or null>",
  "report_md": "## GAIC Image Forensics Report...",  // EN; LLM or template
  "inference_ms": 820,
  "errors": ["HEATMAP_ERROR"]  // optional non-fatal warnings
}
```

**Error Response (example):**

```json
{ "error_code": "MODEL_TIMEOUT", "message": "Inference exceeded 40s.", "hint": "Resize long side < 1024 or choose another model." }
```

**Error Codes (tab‑delimited for Excel copy):**

```
IMG_FORMAT_UNSUPPORTED	400	Only JPG/PNG/WEBP are supported.	Convert the image to JPG/PNG/WEBP.
IMG_TOO_LARGE	400	File exceeds 10MB limit.	Resize or compress the image.
IMG_DECODE_FAILED	400	Image cannot be decoded.	Re-export; avoid CMYK/16-bit PNG.
MODEL_NOT_FOUND	400	Selected model is unavailable.	Choose another model.
MODEL_TIMEOUT	504	Inference exceeded 40s.	Use smaller image or lower stride.
MODEL_ERROR	500	Model raised an exception.	Retry or switch model.
HEATMAP_ERROR	500	Failed to render heatmap.	Heatmap omitted; result still valid.
REPORT_GEN_ERROR	500	Report generation failed.	Template fallback used.
REPORT_GEN_TIMEOUT	504	Report LLM exceeded 2s.	Template fallback used.
INTERNAL_ERROR	500	Unexpected server error.	Retry; contact maintainer if repeated.
```

---

## 6) Front‑end Implementation Details

### 6.1 Components (Gradio)

* `Dropdown model_dd` — choices: `SuSy` (default), `FatFormer`, `DistilDIRE`
  Disabled options shown if back‑end reports missing weights.
* `Image img_in` — `type="numpy"`, `sources=["upload","clipboard","webcam"]`, `image_mode="RGB"`, `height=380`, `label="Upload an image (≤10MB)"`, `tool=None`, `mirror_webcam=False`.
* `Button btn_analyze` — primary.
* `HTML score_card` — big typography; also shows **gray range tag** (Low/Med/High) with active bin bold.
* `Image orig_img`, `Image heat_img` — both `height≈420` with **click‑to‑lightbox** (custom JS hook or `gr.Image` built‑in preview).
* `Accordion acc_exp` + `Markdown exp_md` — explanation collapsed by default.
* `Gallery history_gal` — `columns=5`, `rows=1`, `height=120`.
* `HTML notice_stack` — yellow notices; each notice auto‑dismiss after 5 s.
* `HTML disclaimer` — fixed footer line.

### 6.2 Event Flow

* `btn_analyze.click(handle_infer, [img_in, model_dd], [score_card, orig_img, heat_img, exp_md, notice_stack], api_name="analyze")`
* `history_gal.select(on_pick_history, [], [score_card, orig_img, heat_img, exp_md])` — **no back‑end call**; replay cached result.
* Disable inputs during inference; re‑enable on completion or error.

### 6.3 Notice Handling

* Convert back‑end `errors[]` to yellow bars:

  * `MODEL_TIMEOUT` → *Inference exceeded 40s...*
  * `HEATMAP_ERROR` → *Heatmap omitted due to time constraints.*
  * `REPORT_GEN_*` → *Explanation fallback in use.*
* Multiple notices can stack; each is a `<div class="notice">` appended to `notice_stack`.

### 6.4 History (session‑only)

* Store array of objects in `sessionStorage` under `gaic_history_v1`:

  ```js
  { ts, model, score, report_md, thumb_base64_256, heat_thumb_base64_256 }
  ```
* Maintain at most 5 entries (FIFO).
* Clicking a history card replays the cached assets; **do not** call `/analyze/image`.

### 6.5 Accessibility & Responsiveness

* Contrast‑safe palette; avoid red/green only for scale; score number uses neutral theme.
* Keyboard focus states; `aria-live` region for notices.
* CSS breakpoint < 768 px → single column layout with components stacked.

---

## 7) Back‑end Expectations from UI

* UI always sends **single image** (<= 10 MB) with selected `model`.
* Heatmap checkbox toggles `include_heatmap` flag. For full‑image models (FatFormer/DistilDIRE), server may return `HEATMAP_ERROR` gracefully.
* Server must implement **degrade steps** per SLA above and populate `errors[]` accordingly.
* `score` must be an **integer 0..100** (linear‑mapped, not calibrated) so the UI’s range bins behave consistently across models.

---

## 8) Explanation Generation (UI Contract)

* UI does not generate text; it only renders `report_md` returned by back‑end.
* Collapsed by default; first line of the Markdown is also used as the **one‑line teaser** under the *Show explanation* button.
* If `REPORT_GEN_TIMEOUT/ERROR`, UI shows a notice and still renders the template report.

---

## 9) Visual Design Tokens (suggested)

* **Score**: font‑size 56–72 px desktop; 36–48 px mobile; weight 700.
* **Gray range tag**: small caps `Low | Medium | High`; active bin bold + underline.
* **Heatmap**: overlay alpha 0.5; colormap `viridis` (color‑blind friendly).
* **Notices**: `#FFE69C` background; `#8A6D3B` text; rounded corners; shadow.
* **Buttons**: primary `#2563EB`; hover darken 8%.

---

## 10) Performance Notes

* Image preview uses browser‑side scaling; history thumbnails are downscaled to **max side 256 px** before base64 storage.
* Debounce analyze button to prevent double submits.
* Avoid re‑encoding images client‑side; send original file blob to back‑end.

---

## 11) Security & Privacy (PoC Level)

* No cookies/tokens; session data only in `sessionStorage`.
* No uploads persist on server beyond in‑memory inference.
* Disable external URLs and cross‑origin fetches for now.

---

## 12) Testing Plan (UI)

* **Happy paths**: small image (< 512 px) and large image (~3–10 MB) with each model.
* **Error paths**: wrong format, >10 MB, decode fail, model disabled, timeout.
* **Degrade path**: simulate heatmap omission; ensure notices show and UI still renders score + explanation.
* **Mobile**: iOS Safari webcam capture; Android Chrome drag‑drop.

---

## 13) Implementation Checklist

* [ ] Header with model dropdown and heatmap toggle
* [ ] Yellow notice stack (hidden by default)
* [ ] Upload card (upload/clipboard/webcam; one file; size guard; format guard)
* [ ] Score card (big number + gray range tag + latency + model tag + download report)
* [ ] Side‑by‑side image panel with lightbox
* [ ] Explanation accordion (collapsed; render Markdown)
* [ ] History gallery (5 entries; session‑only)
* [ ] Footer disclaimer (EN)
* [ ] API glue (call `/analyze/image`, map errors → notices)
* [ ] Responsive CSS breakpoints
* [ ] Basic UI tests (manual), smoke script for API connectivity

---

## 14) Future Hooks (Out of Current Scope)

* Video tab (disabled placeholder)
* URL ingestion with fetch + CORS proxy
* i18n (Chinese UI), theme switch (dark mode)
* Downloadable PDF report
* Small on‑device LLM for offline explanation

---

## 15) Quick Start (Dev)

1. **Install** (example):

   ```bash
   pip install gradio==4.* requests
   ```
2. **Run back‑end** (separate): `uvicorn app.main:app --port 8000`
3. **Run GUI**: `python gradio/app.py` (points to `http://localhost:8000/analyze/image`)
4. Open `http://localhost:7860` and test.

---

**End of master_plan.md**
