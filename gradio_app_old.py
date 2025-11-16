"""Gradio UI for GAIC Detector."""

import gradio as gr
import requests
import json
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from typing import Optional, List, Dict, Tuple

# Configuration
API_URL = "http://localhost:8000"
MAX_HISTORY = 5

# Global history storage (session-level)
history_data: List[Dict] = []


def get_range_label(score: int) -> str:
    """Get range label with active bin bolded."""
    if score <= 30:
        return "<span style='color: #666;'><b>Low</b> · Medium · High</span>"
    elif score <= 70:
        return "<span style='color: #666;'>Low · <b>Medium</b> · High</span>"
    else:
        return "<span style='color: #666;'>Low · Medium · <b>High</b></span>"


def format_score_card(score: int, model: str, inference_ms: int) -> str:
    """Format the score card HTML."""
    range_label = get_range_label(score)
    
    html = f"""
    <div style="padding: 30px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
        <div style="font-size: 72px; font-weight: 700; margin-bottom: 10px;">
            {score}
        </div>
        <div style="font-size: 18px; margin-bottom: 15px; opacity: 0.9;">
            {range_label}
        </div>
        <div style="font-size: 14px; opacity: 0.8;">
            Model: <b>{model}</b> | Inference: <b>{inference_ms}ms</b>
        </div>
    </div>
    """
    return html


def format_notices(errors: List[str]) -> str:
    """Format error notices as HTML."""
    if not errors:
        return ""
    
    notice_map = {
        "MODEL_TIMEOUT": "⚠️ Inference exceeded 40s. Results may be incomplete.",
        "HEATMAP_ERROR": "⚠️ Heatmap omitted due to time constraints.",
        "REPORT_GEN_TIMEOUT": "⚠️ Explanation generation timed out. Using template.",
        "REPORT_GEN_ERROR": "⚠️ Explanation fallback in use.",
    }
    
    notices_html = ""
    for error in errors:
        msg = notice_map.get(error, f"⚠️ {error}")
        notices_html += f"""
        <div style="background: #FFE69C; color: #8A6D3B; padding: 12px 20px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #8A6D3B;">
            {msg}
        </div>
        """
    
    return notices_html


def add_to_history(
    score: int,
    model: str,
    report_md: str,
    original_img: Image.Image,
    heatmap_b64: Optional[str]
) -> None:
    """Add result to history."""
    global history_data
    
    # Create thumbnail
    thumb = original_img.copy()
    thumb.thumbnail((256, 256), Image.LANCZOS)
    
    entry = {
        "score": score,
        "model": model,
        "report_md": report_md,
        "original": original_img,
        "heatmap_b64": heatmap_b64,
        "thumbnail": thumb
    }
    
    history_data.insert(0, entry)
    if len(history_data) > MAX_HISTORY:
        history_data = history_data[:MAX_HISTORY]


def analyze_image(
    image: Optional[np.ndarray],
    model: str,
    include_heatmap: bool
) -> Tuple[str, Optional[Image.Image], Optional[Image.Image], str, str]:
    """
    Analyze image and return results.
    
    Returns:
        Tuple of (score_card_html, original_image, heatmap_image, report_md, notices_html)
    """
    if image is None:
        return (
            "<div style='padding: 20px; text-align: center; color: #999;'>Please upload an image</div>",
            None,
            None,
            "",
            ""
        )
    
    try:
        # Convert numpy to PIL
        pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
        
        # Convert to bytes
        img_buffer = BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Call API
        files = {"file": ("image.png", img_bytes, "image/png")}
        data = {
            "model": model,
            "include_heatmap": str(include_heatmap).lower()
        }
        
        response = requests.post(
            f"{API_URL}/analyze/image",
            files=files,
            data=data,
            timeout=45
        )
        
        if response.status_code != 200:
            error_detail = response.json()
            error_msg = error_detail.get("detail", {})
            if isinstance(error_msg, dict):
                msg = f"{error_msg.get('message', 'Unknown error')}<br><i>{error_msg.get('hint', '')}</i>"
            else:
                msg = str(error_msg)
            
            return (
                f"<div style='padding: 20px; text-align: center; color: #d32f2f;'>Error: {msg}</div>",
                pil_image,
                None,
                "",
                format_notices([error_detail.get("error_code", "INTERNAL_ERROR")])
            )
        
        result = response.json()
        
        # Format score card
        score_html = format_score_card(
            result["score"],
            result["model"],
            result["inference_ms"]
        )
        
        # Decode heatmap if present
        heatmap_img = None
        if result.get("heatmap_png_b64"):
            heatmap_bytes = base64.b64decode(result["heatmap_png_b64"])
            heatmap_img = Image.open(BytesIO(heatmap_bytes))
        
        # Format notices
        notices = format_notices(result.get("errors", []))
        
        # Add to history
        add_to_history(
            result["score"],
            result["model"],
            result["report_md"],
            pil_image,
            result.get("heatmap_png_b64")
        )
        
        return (
            score_html,
            pil_image,
            heatmap_img,
            result["report_md"],
            notices
        )
        
    except requests.exceptions.Timeout:
        return (
            "<div style='padding: 20px; text-align: center; color: #d32f2f;'>Request timed out. Please try a smaller image.</div>",
            pil_image if 'pil_image' in locals() else None,
            None,
            "",
            format_notices(["MODEL_TIMEOUT"])
        )
    except Exception as e:
        return (
            f"<div style='padding: 20px; text-align: center; color: #d32f2f;'>Error: {str(e)}</div>",
            pil_image if 'pil_image' in locals() else None,
            None,
            "",
            format_notices(["INTERNAL_ERROR"])
        )


def get_history_gallery() -> List[Image.Image]:
    """Get history thumbnails for gallery."""
    return [entry["thumbnail"] for entry in history_data]


def replay_history(evt: gr.SelectData) -> Tuple[str, Image.Image, Optional[Image.Image], str, str]:
    """Replay a history entry."""
    if not history_data or evt.index >= len(history_data):
        return ("", None, None, "", "")
    
    entry = history_data[evt.index]
    
    # Recreate score card
    score_html = format_score_card(entry["score"], entry["model"], 0)
    
    # Decode heatmap if present
    heatmap_img = None
    if entry.get("heatmap_b64"):
        heatmap_bytes = base64.b64decode(entry["heatmap_b64"])
        heatmap_img = Image.open(BytesIO(heatmap_bytes))
    
    return (
        score_html,
        entry["original"],
        heatmap_img,
        entry["report_md"],
        "<div style='background: #E3F2FD; color: #1976D2; padding: 12px 20px; margin: 8px 0; border-radius: 6px;'>📋 Replayed from history</div>"
    )


# Custom CSS
custom_css = """
.gradio-container {
    max-width: 1400px !important;
}

.score-card {
    margin: 20px 0;
}

.image-container {
    border-radius: 8px;
    overflow: hidden;
}

footer {
    margin-top: 40px !important;
}

.gallery-item {
    cursor: pointer;
}

.disclaimer {
    background: #FFF3E0;
    border-left: 4px solid #FF9800;
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 4px;
    color: #E65100;
}
"""


# Build Gradio interface
with gr.Blocks(css=custom_css, title="GAIC Detector - AI Image Detection") as demo:
    gr.HTML("""
        <div style="text-align: center; padding: 30px 0;">
            <h1 style="font-size: 42px; font-weight: 700; margin-bottom: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🔍 GAIC Detector
            </h1>
            <p style="font-size: 18px; color: #666;">AI-Generated Image Detection for Taiwan FactCheck Center</p>
        </div>
    """)
    
    # Model selector and options
    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=["SuSy", "FatFormer", "DistilDIRE"],
            value="SuSy",
            label="Detection Model",
            info="Select the AI detection model to use"
        )
        heatmap_checkbox = gr.Checkbox(
            value=True,
            label="Include Heatmap",
            info="Generate visual heatmap overlay (may increase processing time)"
        )
    
    # Notice stack
    notices_html = gr.HTML(value="", visible=True)
    
    # Main content
    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                label="Upload Image (≤10MB)",
                type="numpy",
                sources=["upload", "clipboard", "webcam"],
                height=380
            )
            analyze_btn = gr.Button("🔍 Analyze Image", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            score_card = gr.HTML(
                value="<div style='padding: 60px; text-align: center; color: #999; border: 2px dashed #ddd; border-radius: 12px;'>Upload an image to analyze</div>"
            )
    
    # Image comparison
    gr.Markdown("### 📊 Visual Analysis")
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("**Original Image**")
            original_display = gr.Image(label="", height=420, interactive=False)
        
        with gr.Column(scale=1):
            gr.Markdown("**Heatmap Overlay**")
            heatmap_display = gr.Image(label="", height=420, interactive=False)
    
    # Explanation
    with gr.Accordion("📝 Detailed Explanation", open=False):
        explanation_md = gr.Markdown(value="")
    
    # History
    gr.Markdown("### 📜 Recent Analysis History")
    history_gallery = gr.Gallery(
        label="Click to replay",
        show_label=False,
        columns=5,
        rows=1,
        height=140,
        object_fit="cover"
    )
    
    # Footer disclaimer
    gr.HTML("""
        <div class="disclaimer">
            <strong>⚠️ Important Disclaimer:</strong> This score is experimental and non-diagnostic. 
            Results should not be used as the sole basis for determining image authenticity. 
            Multiple factors can influence detection accuracy. For critical applications, 
            consult with forensic experts and use multiple verification methods.
        </div>
        <div style="text-align: center; padding: 20px; color: #999; font-size: 14px;">
            GAIC Detector v1.0 | Taiwan FactCheck Center Demo | 
            <a href="https://github.com/thedannyliu/GAIC-Detector-Web-GUI" target="_blank" style="color: #667eea;">GitHub</a>
        </div>
    """)
    
    # Event handlers
    analyze_btn.click(
        fn=analyze_image,
        inputs=[image_input, model_dropdown, heatmap_checkbox],
        outputs=[score_card, original_display, heatmap_display, explanation_md, notices_html]
    ).then(
        fn=get_history_gallery,
        inputs=[],
        outputs=[history_gallery]
    )
    
    history_gallery.select(
        fn=replay_history,
        inputs=[],
        outputs=[score_card, original_display, heatmap_display, explanation_md, notices_html]
    )


if __name__ == "__main__":
    import os
    
    # Check if we should enable sharing (for cluster environments)
    enable_share = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=enable_share  # Set to True to get a public URL
    )
