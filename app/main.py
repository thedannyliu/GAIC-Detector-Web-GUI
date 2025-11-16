"""FastAPI backend for GAIC Detector - AIDE + Grad-CAM + Video Support."""

import time
import base64
from io import BytesIO
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import (
    MAX_IMAGE_SIZE_BYTES,
    MAX_VIDEO_SIZE_BYTES,
    MODEL_NAME,
    TIMEOUT_TOTAL,
    GRADCAM_COLORMAP,
    GRADCAM_ALPHA
)
from app.errors import GAICException, ErrorCode
from app.image_utils import (
    validate_image_format,
    load_and_preprocess_image,
    create_gradcam_overlay
)
from app.video_utils import (
    validate_video_format,
    sample_frames_from_video,
    frame_to_pil
)
from app.aide_inference import run_inference  # Real AIDE model
from app.report import generate_report


app = FastAPI(
    title="GAIC Detector API - AIDE Edition",
    description="AI-Generated Content Detection API with AIDE model and Grad-CAM",
    version="2.0.0"
)

# CORS middleware for Gradio frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeImageResponse(BaseModel):
    """Response model for /analyze/image endpoint."""
    score: int
    model: str
    heatmap_png_b64: Optional[str]
    report_md: str
    inference_ms: int
    errors: List[str] = []


class AnalyzeVideoResponse(BaseModel):
    """Response model for /analyze/video endpoint."""
    score: int
    model: str
    key_frame_index: int
    key_frame_ts: float
    key_frame_png_b64: str
    heatmap_png_b64: Optional[str]
    report_md: str
    inference_ms: int
    errors: List[str] = []


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "GAIC Detector API - AIDE Edition",
        "version": "2.0.0",
        "model": MODEL_NAME,
        "features": ["image_analysis", "video_analysis", "gradcam", "gemini_reports"]
    }


@app.get("/models")
async def list_models():
    """List available models."""
    return {
        "models": [MODEL_NAME],
        "default": MODEL_NAME,
        "description": "AIDE: AI-generated Image DEtector with Hybrid Features (ResNet-50 based)"
    }


@app.post("/analyze/image", response_model=AnalyzeImageResponse)
async def analyze_image(
    file: UploadFile = File(...),
    include_heatmap: bool = Form(True)
):
    """
    Analyze an image for AI generation likelihood using AIDE + Grad-CAM.
    
    Args:
        file: Image file (JPG/PNG/WEBP, <= 10MB)
        include_heatmap: Whether to generate Grad-CAM heatmap (default: True)
        
    Returns:
        AnalyzeImageResponse with score, heatmap, and report
    """
    errors = []
    start_time = time.time()
    
    try:
        # Validate file format
        validate_image_format(file.filename or "")
        
        # Read file
        file_bytes = await file.read()
        
        # Validate file size
        if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
            raise GAICException(ErrorCode.IMG_TOO_LARGE)
        
        # Load and preprocess image
        image_array, pil_image = load_and_preprocess_image(file_bytes)
        
        # Run AIDE inference with Grad-CAM
        try:
            fake_prob, gradcam_heatmap, inference_ms = run_inference(
                image_array,
                include_heatmap=include_heatmap,
                timeout=TIMEOUT_TOTAL
            )
        except GAICException as e:
            if e.error_code == ErrorCode.MODEL_TIMEOUT:
                raise
            errors.append(e.error_code)
            # For demo, use fallback values
            fake_prob = 0.5
            gradcam_heatmap = None
            inference_ms = int((time.time() - start_time) * 1000)
        
        # Convert score to 0-100 integer
        score = int(fake_prob * 100)
        
        # Generate Grad-CAM overlay
        heatmap_b64 = None
        if include_heatmap and gradcam_heatmap is not None:
            try:
                heatmap_b64 = create_gradcam_overlay(
                    pil_image,
                    gradcam_heatmap,
                    alpha=GRADCAM_ALPHA,
                    colormap=GRADCAM_COLORMAP
                )
                if heatmap_b64 is None:
                    errors.append(ErrorCode.HEATMAP_ERROR)
            except Exception as e:
                print(f"Heatmap overlay error: {e}")
                errors.append(ErrorCode.HEATMAP_ERROR)
        
        # Generate report with Gemini
        report_md, report_error = await generate_report(
            score,
            MODEL_NAME,
            media_type="image"
        )
        if report_error:
            errors.append(report_error)
        
        # Check total time
        elapsed = time.time() - start_time
        if elapsed > TIMEOUT_TOTAL:
            raise GAICException(ErrorCode.MODEL_TIMEOUT)
        
        return AnalyzeImageResponse(
            score=score,
            model=MODEL_NAME,
            heatmap_png_b64=heatmap_b64,
            report_md=report_md,
            inference_ms=inference_ms,
            errors=errors
        )
        
    except GAICException as e:
        raise e.to_http_exception()
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": ErrorCode.INTERNAL_ERROR,
                "message": str(e),
                "hint": "Retry; contact maintainer if repeated."
            }
        )


@app.post("/analyze/video", response_model=AnalyzeVideoResponse)
async def analyze_video(
    file: UploadFile = File(...),
    include_heatmap: bool = Form(True)
):
    """
    Analyze a video for AI generation likelihood using AIDE + Grad-CAM on sampled frames.
    
    Args:
        file: Video file (MP4/MOV/WEBM, <= 50MB)
        include_heatmap: Whether to generate Grad-CAM heatmap (default: True)
        
    Returns:
        AnalyzeVideoResponse with video-level score, key frame, heatmap, and report
    """
    errors = []
    start_time = time.time()
    
    try:
        # Validate file format
        validate_video_format(file.filename or "")
        
        # Read file
        file_bytes = await file.read()
        
        # Validate file size
        if len(file_bytes) > MAX_VIDEO_SIZE_BYTES:
            raise GAICException(ErrorCode.VIDEO_TOO_LARGE)
        
        # Sample frames from video
        try:
            frames, timestamps, duration = sample_frames_from_video(file_bytes)
        except GAICException:
            raise
        except Exception as e:
            raise GAICException(ErrorCode.VIDEO_DECODE_FAILED, str(e))
        
        # Analyze each frame with AIDE
        frame_results = []
        for idx, (frame, ts) in enumerate(zip(frames, timestamps)):
            try:
                fake_prob, gradcam_heatmap, _ = run_inference(
                    frame,
                    include_heatmap=include_heatmap,
                    timeout=TIMEOUT_TOTAL / len(frames)  # Per-frame timeout
                )
                
                frame_results.append({
                    "index": idx,
                    "timestamp": ts,
                    "score": int(fake_prob * 100),
                    "fake_prob": fake_prob,
                    "heatmap": gradcam_heatmap,
                    "frame": frame
                })
            except Exception as e:
                print(f"Frame {idx} analysis failed: {e}")
                # Skip failed frames
                continue
        
        if len(frame_results) == 0:
            raise GAICException(ErrorCode.MODEL_ERROR, "No frames analyzed successfully")
        
        # Aggregate: video score = max of frame scores
        frame_results.sort(key=lambda x: x["score"], reverse=True)
        key_frame = frame_results[0]  # Most suspicious frame
        video_score = key_frame["score"]
        
        # Generate key frame PNG
        key_frame_pil = frame_to_pil(key_frame["frame"])
        key_frame_buffer = BytesIO()
        key_frame_pil.save(key_frame_buffer, format='PNG')
        key_frame_png_b64 = base64.b64encode(key_frame_buffer.getvalue()).decode('utf-8')
        
        # Generate key frame Grad-CAM overlay
        heatmap_b64 = None
        if include_heatmap and key_frame["heatmap"] is not None:
            try:
                heatmap_b64 = create_gradcam_overlay(
                    key_frame_pil,
                    key_frame["heatmap"],
                    alpha=GRADCAM_ALPHA,
                    colormap=GRADCAM_COLORMAP
                )
                if heatmap_b64 is None:
                    errors.append(ErrorCode.HEATMAP_ERROR)
            except Exception as e:
                print(f"Heatmap overlay error: {e}")
                errors.append(ErrorCode.HEATMAP_ERROR)
        
        # Prepare context for Gemini report (top 3 frames)
        top_frames_context = {
            "num_frames": len(frames),
            "frames": [
                {
                    "timestamp": fr["timestamp"],
                    "score": fr["score"]
                }
                for fr in frame_results[:3]
            ]
        }
        
        # Generate report with Gemini
        report_md, report_error = await generate_report(
            video_score,
            MODEL_NAME,
            media_type="video",
            extra_context=top_frames_context
        )
        if report_error:
            errors.append(report_error)
        
        # Calculate total inference time
        elapsed = time.time() - start_time
        inference_ms = int(elapsed * 1000)
        
        # Check total time
        if elapsed > TIMEOUT_TOTAL:
            raise GAICException(ErrorCode.MODEL_TIMEOUT)
        
        return AnalyzeVideoResponse(
            score=video_score,
            model=MODEL_NAME,
            key_frame_index=key_frame["index"],
            key_frame_ts=key_frame["timestamp"],
            key_frame_png_b64=key_frame_png_b64,
            heatmap_png_b64=heatmap_b64,
            report_md=report_md,
            inference_ms=inference_ms,
            errors=errors
        )
        
    except GAICException as e:
        raise e.to_http_exception()
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": ErrorCode.INTERNAL_ERROR,
                "message": str(e),
                "hint": "Retry; contact maintainer if repeated."
            }
        )


if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT
    
    print(f"Starting GAIC Detector API - AIDE Edition")
    print(f"Model: {MODEL_NAME}")
    print(f"Features: Image + Video analysis with Grad-CAM")
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
