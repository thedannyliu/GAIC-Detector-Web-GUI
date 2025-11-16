"""Gradio UI for GAIC Detector - AIDE Edition with Image and Video Support."""

import os
import gradio as gr
import requests
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from typing import Optional, List, Dict, Tuple

# Configuration
API_URL = os.getenv("GAIC_BACKEND_URL", "http://localhost:8000")
MAX_HISTORY = 5

# Global history storage (session-level) - separate for image and video
image_history: List[Dict] = []
video_history: List[Dict] = []


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_range_label(score: int) -> str:
    """Get range label with active bin bolded."""
    if score <= 30:
        return "<span style='color: #666;'><b>Low (0–30)</b> · Medium (30–70) · High (70–100)</span>"
    elif score <= 70:
        return "<span style='color: #666;'>Low (0–30) · <b>Medium (30–70)</b> · High (70–100)</span>"
    else:
        return "<span style='color: #666;'>Low (0–30) · Medium (30–70) · <b>High (70–100)</b></span>"


def format_score_card(score: int, model: str, inference_ms: int, media_type: str = "image") -> str:
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
            Model: <b>{model}</b> | Type: <b>{media_type.upper()}</b> | Inference: <b>{inference_ms}ms</b>
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
        "HEATMAP_ERROR": "⚠️ Grad-CAM heatmap generation failed.",
        "REPORT_GEN_TIMEOUT": "⚠️ Gemini explanation timed out. Using template.",
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


# ============================================
# IMAGE ANALYSIS FUNCTIONS
# ============================================

def analyze_image(
    image: Optional[np.ndarray],
    include_heatmap: bool
) -> Tuple[str, Optional[Image.Image], Optional[Image.Image], str, str, List]:
    """
    Analyze image and return results.
    
    Returns:
        Tuple of (score_card_html, original_image, heatmap_image, report_md, notices_html, history_gallery)
    """
    if image is None:
        return (
            "<div style='padding: 20px; text-align: center; color: #999;'>Please upload an image</div>",
            None,
            None,
            "",
            "",
            get_image_history_gallery()
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
        data = {"include_heatmap": str(include_heatmap).lower()}
        
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
                format_notices([error_detail.get("error_code", "INTERNAL_ERROR")]),
                get_image_history_gallery()
            )
        
        result = response.json()
        
        # Format score card
        score_html = format_score_card(
            result["score"],
            result["model"],
            result["inference_ms"],
            media_type="image"
        )
        
        # Decode heatmap if present
        heatmap_img = None
        if result.get("heatmap_png_b64"):
            heatmap_bytes = base64.b64decode(result["heatmap_png_b64"])
            heatmap_img = Image.open(BytesIO(heatmap_bytes))
        
        # Format notices
        notices = format_notices(result.get("errors", []))
        
        # Add to history
        add_to_image_history(
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
            notices,
            get_image_history_gallery()
        )
        
    except requests.exceptions.Timeout:
        return (
            "<div style='padding: 20px; text-align: center; color: #d32f2f;'>Request timed out. Please try a smaller image.</div>",
            pil_image if 'pil_image' in locals() else None,
            None,
            "",
            format_notices(["MODEL_TIMEOUT"]),
            get_image_history_gallery()
        )
    except Exception as e:
        return (
            f"<div style='padding: 20px; text-align: center; color: #d32f2f;'>Error: {str(e)}</div>",
            pil_image if 'pil_image' in locals() else None,
            None,
            "",
            format_notices(["INTERNAL_ERROR"]),
            get_image_history_gallery()
        )


def add_to_image_history(
    score: int,
    model: str,
    report_md: str,
    original_img: Image.Image,
    heatmap_b64: Optional[str]
) -> None:
    """Add image result to history."""
    global image_history
    
    # Create thumbnail
    thumb = original_img.copy()
    thumb.thumbnail((256, 256), Image.Resampling.LANCZOS)
    
    entry = {
        "score": score,
        "model": model,
        "report_md": report_md,
        "original": original_img,
        "heatmap_b64": heatmap_b64,
        "thumbnail": thumb
    }
    
    image_history.insert(0, entry)
    if len(image_history) > MAX_HISTORY:
        image_history = image_history[:MAX_HISTORY]


def get_image_history_gallery() -> List:
    """Get image history thumbnails for gallery."""
    return [entry["thumbnail"] for entry in image_history]


def replay_image_history(evt: gr.SelectData) -> Tuple[str, Image.Image, Optional[Image.Image], str, str]:
    """Replay an image history entry."""
    if not image_history or evt.index >= len(image_history):
        return ("", None, None, "", "")
    
    entry = image_history[evt.index]
    
    # Recreate score card
    score_html = format_score_card(entry["score"], entry["model"], 0, "image")
    
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


# ============================================
# VIDEO ANALYSIS FUNCTIONS
# ============================================

def analyze_video(
    video_file,
    include_heatmap: bool
) -> Tuple[str, Optional[Image.Image], Optional[Image.Image], str, str, str, List]:
    """
    Analyze video and return results.
    
    Returns:
        Tuple of (score_card_html, key_frame_image, heatmap_image, frame_info_html, report_md, notices_html, history_gallery)
    """
    if video_file is None:
        return (
            "<div style='padding: 20px; text-align: center; color: #999;'>Please upload a video</div>",
            None,
            None,
            "",
            "",
            "",
            get_video_history_gallery()
        )
    
    try:
        # Read video file
        with open(video_file, 'rb') as f:
            video_bytes = f.read()
        
        # Call API
        files = {"file": ("video.mp4", video_bytes, "video/mp4")}
        data = {"include_heatmap": str(include_heatmap).lower()}
        
        response = requests.post(
            f"{API_URL}/analyze/video",
            files=files,
            data=data,
            timeout=50
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
                None,
                None,
                "",
                "",
                format_notices([error_detail.get("error_code", "INTERNAL_ERROR")]),
                get_video_history_gallery()
            )
        
        result = response.json()
        
        # Format score card
        score_html = format_score_card(
            result["score"],
            result["model"],
            result["inference_ms"],
            media_type="video"
        )
        
        # Decode key frame
        key_frame_bytes = base64.b64decode(result["key_frame_png_b64"])
        key_frame_img = Image.open(BytesIO(key_frame_bytes))
        
        # Decode heatmap if present
        heatmap_img = None
        if result.get("heatmap_png_b64"):
            heatmap_bytes = base64.b64decode(result["heatmap_png_b64"])
            heatmap_img = Image.open(BytesIO(heatmap_bytes))
        
        # Format frame info
        frame_info = f"""
        <div style="padding: 10px; background: #f5f5f5; border-radius: 6px; margin: 10px 0;">
            <b>Key Frame Info:</b> Frame #{result["key_frame_index"]} at ~{result["key_frame_ts"]:.1f}s
        </div>
        """
        
        # Format notices
        notices = format_notices(result.get("errors", []))
        
        # Add to history
        add_to_video_history(
            result["score"],
            result["model"],
            result["report_md"],
            key_frame_img,
            result.get("heatmap_png_b64"),
            result["key_frame_ts"]
        )
        
        return (
            score_html,
            key_frame_img,
            heatmap_img,
            frame_info,
            result["report_md"],
            notices,
            get_video_history_gallery()
        )
        
    except requests.exceptions.Timeout:
        return (
            "<div style='padding: 20px; text-align: center; color: #d32f2f;'>Request timed out. Please try a smaller video.</div>",
            None,
            None,
            "",
            "",
            format_notices(["MODEL_TIMEOUT"]),
            get_video_history_gallery()
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return (
            f"<div style='padding: 20px; text-align: center; color: #d32f2f;'>Error: {str(e)}</div>",
            None,
            None,
            "",
            "",
            format_notices(["INTERNAL_ERROR"]),
            get_video_history_gallery()
        )


def add_to_video_history(
    score: int,
    model: str,
    report_md: str,
    key_frame_img: Image.Image,
    heatmap_b64: Optional[str],
    timestamp: float
) -> None:
    """Add video result to history."""
    global video_history
    
    # Create thumbnail
    thumb = key_frame_img.copy()
    thumb.thumbnail((256, 256), Image.Resampling.LANCZOS)
    
    entry = {
        "score": score,
        "model": model,
        "report_md": report_md,
        "key_frame": key_frame_img,
        "heatmap_b64": heatmap_b64,
        "timestamp": timestamp,
        "thumbnail": thumb
    }
    
    video_history.insert(0, entry)
    if len(video_history) > MAX_HISTORY:
        video_history = video_history[:MAX_HISTORY]


def get_video_history_gallery() -> List:
    """Get video history thumbnails for gallery."""
    return [entry["thumbnail"] for entry in video_history]


def replay_video_history(evt: gr.SelectData) -> Tuple[str, Image.Image, Optional[Image.Image], str, str, str]:
    """Replay a video history entry."""
    if not video_history or evt.index >= len(video_history):
        return ("", None, None, "", "", "")
    
    entry = video_history[evt.index]
    
    # Recreate score card
    score_html = format_score_card(entry["score"], entry["model"], 0, "video")
    
    # Decode heatmap if present
    heatmap_img = None
    if entry.get("heatmap_b64"):
        heatmap_bytes = base64.b64decode(entry["heatmap_b64"])
        heatmap_img = Image.open(BytesIO(heatmap_bytes))
    
    # Frame info
    frame_info = f"""
    <div style="padding: 10px; background: #f5f5f5; border-radius: 6px; margin: 10px 0;">
        <b>Key Frame:</b> ~{entry["timestamp"]:.1f}s
    </div>
    """
    
    return (
        score_html,
        entry["key_frame"],
        heatmap_img,
        frame_info,
        entry["report_md"],
        "<div style='background: #E3F2FD; color: #1976D2; padding: 12px 20px; margin: 8px 0; border-radius: 6px;'>📋 Replayed from history</div>"
    )


# ============================================
# GRADIO UI
# ============================================

# Custom CSS
custom_css = """
.gradio-container {
    max-width: 1400px !important;
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

# Build Gradio interface with Tabs
with gr.Blocks(css=custom_css, title="GAIC Detector - AIDE Edition") as demo:
    # Header
    gr.HTML("""
        <div style="text-align: center; padding: 30px 0;">
            <h1 style="font-size: 42px; font-weight: 700; margin-bottom: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🔍 GAIC Detector
            </h1>
            <p style="font-size: 18px; color: #666;">AI-Generated Content Detection | Taiwan FactCheck Center</p>
            <p style="font-size: 14px; color: #999;">Powered by AIDE + Grad-CAM + Gemini</p>
        </div>
    """)
    
    with gr.Tabs() as tabs:
        # ============================================
        # IMAGE TAB
        # ============================================
        with gr.Tab("📷 Image Analysis"):
            with gr.Row():
                gr.HTML("<h3>Settings</h3>")
                heatmap_checkbox_img = gr.Checkbox(
                    value=True,
                    label="Include Grad-CAM Heatmap",
                    info="Generate visual explanation overlay"
                )
            
            notices_html_img = gr.HTML(value="", visible=True)
            
            with gr.Row():
                with gr.Column(scale=1):
                    image_input = gr.Image(
                        label="Upload Image (≤10MB)",
                        type="numpy",
                        sources=["upload", "clipboard", "webcam"],
                        height=380
                    )
                    analyze_btn_img = gr.Button("🔍 Analyze Image", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    score_card_img = gr.HTML(
                        value="<div style='padding: 60px; text-align: center; color: #999; border: 2px dashed #ddd; border-radius: 12px;'>Upload an image to analyze</div>"
                    )
            
            gr.Markdown("### 📊 Visual Analysis")
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("**Original Image**")
                    original_display_img = gr.Image(label="", height=420, interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("**Grad-CAM Heatmap**")
                    heatmap_display_img = gr.Image(label="", height=420, interactive=False)
            
            with gr.Accordion("📝 Detailed Explanation", open=False):
                explanation_md_img = gr.Markdown(value="")
            
            gr.Markdown("### 📜 Recent Analysis History")
            history_gallery_img = gr.Gallery(
                label="Click to replay",
                show_label=False,
                columns=5,
                rows=1,
                height=140,
                object_fit="cover"
            )
        
        # ============================================
        # VIDEO TAB
        # ============================================
        with gr.Tab("🎥 Video Analysis"):
            with gr.Row():
                gr.HTML("<h3>Settings</h3>")
                heatmap_checkbox_vid = gr.Checkbox(
                    value=True,
                    label="Include Grad-CAM Heatmap",
                    info="Generate visual explanation overlay"
                )
            
            notices_html_vid = gr.HTML(value="", visible=True)
            
            with gr.Row():
                with gr.Column(scale=1):
                    video_input = gr.Video(
                        label="Upload Video (≤50MB, MP4/MOV/WEBM)",
                        height=380
                    )
                    analyze_btn_vid = gr.Button("🔍 Analyze Video", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    score_card_vid = gr.HTML(
                        value="<div style='padding: 60px; text-align: center; color: #999; border: 2px dashed #ddd; border-radius: 12px;'>Upload a video to analyze</div>"
                    )
            
            gr.Markdown("### 📊 Key Frame Analysis")
            frame_info_html_vid = gr.HTML(value="")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("**Key Frame**")
                    key_frame_display_vid = gr.Image(label="", height=420, interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("**Grad-CAM Heatmap**")
                    heatmap_display_vid = gr.Image(label="", height=420, interactive=False)
            
            with gr.Accordion("📝 Detailed Explanation", open=False):
                explanation_md_vid = gr.Markdown(value="")
            
            gr.Markdown("### 📜 Recent Analysis History")
            history_gallery_vid = gr.Gallery(
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
            Please do not treat it as conclusive evidence. Results should not be used as the sole basis 
            for determining content authenticity. For critical applications, consult with forensic experts 
            and use multiple verification methods.
        </div>
        <div style="text-align: center; padding: 20px; color: #999; font-size: 14px;">
            GAIC Detector v2.0 - AIDE Edition | Taiwan FactCheck Center Demo | 
            <a href="https://github.com/thedannyliu/GAIC-Detector-Web-GUI" target="_blank" style="color: #667eea;">GitHub</a>
        </div>
    """)
    
    # Event handlers - Image
    analyze_btn_img.click(
        fn=analyze_image,
        inputs=[image_input, heatmap_checkbox_img],
        outputs=[
            score_card_img,
            original_display_img,
            heatmap_display_img,
            explanation_md_img,
            notices_html_img,
            history_gallery_img
        ]
    )
    
    history_gallery_img.select(
        fn=replay_image_history,
        inputs=[],
        outputs=[
            score_card_img,
            original_display_img,
            heatmap_display_img,
            explanation_md_img,
            notices_html_img
        ]
    )
    
    # Event handlers - Video
    analyze_btn_vid.click(
        fn=analyze_video,
        inputs=[video_input, heatmap_checkbox_vid],
        outputs=[
            score_card_vid,
            key_frame_display_vid,
            heatmap_display_vid,
            frame_info_html_vid,
            explanation_md_vid,
            notices_html_vid,
            history_gallery_vid
        ]
    )
    
    history_gallery_vid.select(
        fn=replay_video_history,
        inputs=[],
        outputs=[
            score_card_vid,
            key_frame_display_vid,
            heatmap_display_vid,
            frame_info_html_vid,
            explanation_md_vid,
            notices_html_vid
        ]
    )


if __name__ == "__main__":
    # Check if we should enable sharing (for cluster environments)
    enable_share = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    print("="*60)
    print("GAIC Detector - AIDE Edition")
    print("="*60)
    print(f"Backend API: {API_URL}")
    print(f"Share mode: {enable_share}")
    print("Features:")
    print("  - Image analysis with AIDE + Grad-CAM")
    print("  - Video analysis with frame sampling")
    print("  - Gemini-powered explanations")
    print("  - Session-based history (max 5 per mode)")
    print("="*60)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=enable_share
    )
