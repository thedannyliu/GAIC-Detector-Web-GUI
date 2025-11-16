"""Error codes and exception classes for GAIC Detector API."""

from typing import Optional
from fastapi import HTTPException


class ErrorCode:
    """Error code constants matching master plan."""
    
    # Image errors
    IMG_FORMAT_UNSUPPORTED = "IMG_FORMAT_UNSUPPORTED"
    IMG_TOO_LARGE = "IMG_TOO_LARGE"
    IMG_DECODE_FAILED = "IMG_DECODE_FAILED"
    
    # Video errors
    VIDEO_FORMAT_UNSUPPORTED = "VIDEO_FORMAT_UNSUPPORTED"
    VIDEO_TOO_LARGE = "VIDEO_TOO_LARGE"
    VIDEO_DECODE_FAILED = "VIDEO_DECODE_FAILED"
    VIDEO_TOO_LONG = "VIDEO_TOO_LONG"
    
    # Model errors
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MODEL_ERROR = "MODEL_ERROR"
    
    # Processing errors
    HEATMAP_ERROR = "HEATMAP_ERROR"
    REPORT_GEN_ERROR = "REPORT_GEN_ERROR"
    REPORT_GEN_TIMEOUT = "REPORT_GEN_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


ERROR_MESSAGES = {
    ErrorCode.IMG_FORMAT_UNSUPPORTED: {
        "status": 400,
        "message": "Only JPG/PNG/WEBP are supported.",
        "hint": "Convert the image to JPG/PNG/WEBP."
    },
    ErrorCode.IMG_TOO_LARGE: {
        "status": 400,
        "message": "File exceeds 10MB limit.",
        "hint": "Resize or compress the image."
    },
    ErrorCode.IMG_DECODE_FAILED: {
        "status": 400,
        "message": "Image cannot be decoded.",
        "hint": "Re-export; avoid CMYK/16-bit PNG."
    },
    ErrorCode.VIDEO_FORMAT_UNSUPPORTED: {
        "status": 400,
        "message": "Only MP4/MOV/WEBM are supported.",
        "hint": "Convert the video to MP4/MOV/WEBM."
    },
    ErrorCode.VIDEO_TOO_LARGE: {
        "status": 400,
        "message": "File exceeds 50MB limit.",
        "hint": "Resize or compress the video."
    },
    ErrorCode.VIDEO_DECODE_FAILED: {
        "status": 400,
        "message": "Video cannot be decoded.",
        "hint": "Re-export; avoid unsupported codecs."
    },
    ErrorCode.VIDEO_TOO_LONG: {
        "status": 400,
        "message": "Video exceeds maximum duration.",
        "hint": "Trim video to under 5 minutes."
    },
    ErrorCode.MODEL_NOT_FOUND: {
        "status": 400,
        "message": "Selected model is unavailable.",
        "hint": "Model AIDE is not loaded."
    },
    ErrorCode.MODEL_TIMEOUT: {
        "status": 504,
        "message": "Inference exceeded 40s.",
        "hint": "Use smaller image/video or lower resolution."
    },
    ErrorCode.MODEL_ERROR: {
        "status": 500,
        "message": "Model raised an exception.",
        "hint": "Retry; contact maintainer if repeated."
    },
    ErrorCode.HEATMAP_ERROR: {
        "status": 500,
        "message": "Failed to render Grad-CAM heatmap.",
        "hint": "Heatmap omitted; score still valid."
    },
    ErrorCode.REPORT_GEN_ERROR: {
        "status": 500,
        "message": "Report generation failed.",
        "hint": "Template fallback used."
    },
    ErrorCode.REPORT_GEN_TIMEOUT: {
        "status": 504,
        "message": "Report LLM exceeded 2s.",
        "hint": "Template fallback used."
    },
    ErrorCode.INTERNAL_ERROR: {
        "status": 500,
        "message": "Unexpected server error.",
        "hint": "Retry; contact maintainer if repeated."
    }
}


class GAICException(Exception):
    """Base exception for GAIC Detector."""
    
    def __init__(self, error_code: str, detail: Optional[str] = None):
        self.error_code = error_code
        error_info = ERROR_MESSAGES.get(error_code, ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR])
        self.status_code = error_info["status"]
        self.message = detail or error_info["message"]
        self.hint = error_info["hint"]
        super().__init__(self.message)
    
    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "error_code": self.error_code,
                "message": self.message,
                "hint": self.hint
            }
        )
