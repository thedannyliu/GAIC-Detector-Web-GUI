"""FastAPI backend for GAIC Detector."""

import time
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import (
    MAX_FILE_SIZE_BYTES,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    TIMEOUT_TOTAL
)
from app.errors import GAICException, ErrorCode
from app.image_utils import (
    validate_image_format,
    load_and_preprocess_image,
    create_heatmap_overlay
)
from app.models import run_inference
from app.report import generate_report


app = FastAPI(
    title="GAIC Detector API",
    description="AI-Generated Image Detection API for Taiwan FactCheck Center",
    version="1.0.0"
)

# CORS middleware for Gradio frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeResponse(BaseModel):
    """Response model for /analyze/image endpoint."""
    score: int
    model: str
    heatmap_png_b64: Optional[str]
    report_md: str
    inference_ms: int
    errors: List[str] = []


class ErrorResponse(BaseModel):
    """Error response model."""
    error_code: str
    message: str
    hint: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "GAIC Detector API",
        "version": "1.0.0",
        "available_models": AVAILABLE_MODELS
    }


@app.get("/models")
async def list_models():
    """List available models."""
    return {
        "models": AVAILABLE_MODELS,
        "default": DEFAULT_MODEL
    }


@app.post("/analyze/image", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    model: str = Form(DEFAULT_MODEL),
    include_heatmap: bool = Form(True)
):
    """
    Analyze an image for AI generation likelihood.
    
    Args:
        file: Image file (JPG/PNG/WEBP, <= 10MB)
        model: Model name (SuSy, FatFormer, or DistilDIRE)
        include_heatmap: Whether to generate heatmap overlay
        
    Returns:
        AnalyzeResponse with score, heatmap, and report
    """
    errors = []
    start_time = time.time()
    
    try:
        # Validate model
        if model not in AVAILABLE_MODELS:
            raise GAICException(ErrorCode.MODEL_NOT_FOUND)
        
        # Validate file format
        validate_image_format(file.filename or "")
        
        # Read file
        file_bytes = await file.read()
        
        # Validate file size
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise GAICException(ErrorCode.IMG_TOO_LARGE)
        
        # Load and preprocess image
        image_array, pil_image = load_and_preprocess_image(file_bytes)
        
        # Run inference with timeout handling
        try:
            score_01, heatmap, inference_ms = run_inference(
                image_array,
                model,
                include_heatmap=include_heatmap,
                timeout=TIMEOUT_TOTAL
            )
        except GAICException as e:
            if e.error_code == ErrorCode.MODEL_TIMEOUT:
                raise
            errors.append(e.error_code)
            # Continue with mock values for demo
            score_01 = 0.5
            heatmap = None
            inference_ms = int((time.time() - start_time) * 1000)
        
        # Convert score to 0-100 integer
        score = int(score_01 * 100)
        
        # Generate heatmap overlay
        heatmap_b64 = None
        if include_heatmap and heatmap is not None:
            try:
                heatmap_b64 = create_heatmap_overlay(pil_image, heatmap)
                if heatmap_b64 is None:
                    errors.append(ErrorCode.HEATMAP_ERROR)
            except Exception as e:
                print(f"Heatmap error: {e}")
                errors.append(ErrorCode.HEATMAP_ERROR)
        
        # Generate report
        report_md, report_error = await generate_report(score, model)
        if report_error:
            errors.append(report_error)
        
        # Check total time
        elapsed = time.time() - start_time
        if elapsed > TIMEOUT_TOTAL:
            raise GAICException(ErrorCode.MODEL_TIMEOUT)
        
        return AnalyzeResponse(
            score=score,
            model=model,
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
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
