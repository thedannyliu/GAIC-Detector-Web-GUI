"""Video processing utilities for GAIC Detector."""

import cv2
import numpy as np
from typing import List, Tuple
from PIL import Image

from app.config import (
    SUPPORTED_VIDEO_FORMATS,
    VIDEO_SAMPLE_FRAMES,
    VIDEO_MAX_DURATION
)
from app.errors import GAICException, ErrorCode


def validate_video_format(filename: str) -> None:
    """Validate video file format."""
    ext = filename.lower().split('.')[-1]
    if ext not in SUPPORTED_VIDEO_FORMATS:
        raise GAICException(ErrorCode.VIDEO_FORMAT_UNSUPPORTED)


def sample_frames_from_video(
    video_bytes: bytes,
    num_frames: int = VIDEO_SAMPLE_FRAMES
) -> Tuple[List[np.ndarray], List[float], float]:
    """
    Sample frames uniformly from video.
    
    Args:
        video_bytes: Video file as bytes
        num_frames: Number of frames to sample
        
    Returns:
        Tuple of:
        - List of frame arrays (RGB, numpy uint8)
        - List of frame timestamps (seconds)
        - Total video duration (seconds)
    
    Raises:
        GAICException: If video cannot be decoded or exceeds limits
    """
    import tempfile
    import os
    
    try:
        # Write video bytes to temporary file (OpenCV needs file path)
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        
        try:
            # Open video
            cap = cv2.VideoCapture(tmp_path)
            
            if not cap.isOpened():
                raise GAICException(ErrorCode.VIDEO_DECODE_FAILED)
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            # Validate duration
            if duration > VIDEO_MAX_DURATION:
                cap.release()
                raise GAICException(ErrorCode.VIDEO_TOO_LONG)
            
            # Calculate frame indices to sample
            if total_frames < num_frames:
                # If video has fewer frames than requested, sample all
                frame_indices = list(range(total_frames))
            else:
                # Sample uniformly across the video
                step = total_frames / num_frames
                frame_indices = [int(i * step) for i in range(num_frames)]
            
            frames = []
            timestamps = []
            
            for idx in frame_indices:
                # Set frame position
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Convert BGR (OpenCV) to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Calculate timestamp
                timestamp = idx / fps if fps > 0 else 0
                
                frames.append(frame_rgb)
                timestamps.append(timestamp)
            
            cap.release()
            
            if len(frames) == 0:
                raise GAICException(ErrorCode.VIDEO_DECODE_FAILED, "No frames extracted")
            
            return frames, timestamps, duration
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except GAICException:
        raise
    except Exception as e:
        raise GAICException(ErrorCode.VIDEO_DECODE_FAILED, str(e))


def frame_to_pil(frame: np.ndarray) -> Image.Image:
    """Convert numpy frame (RGB) to PIL Image."""
    return Image.fromarray(frame.astype('uint8'), 'RGB')


def resize_frame(frame: np.ndarray, target_size: int) -> np.ndarray:
    """
    Resize frame to target size while maintaining aspect ratio.
    
    Args:
        frame: RGB numpy array
        target_size: Target size for longer side
        
    Returns:
        Resized frame (RGB numpy array)
    """
    h, w = frame.shape[:2]
    if max(h, w) <= target_size:
        return frame
    
    if h > w:
        new_h = target_size
        new_w = int(w * target_size / h)
    else:
        new_w = target_size
        new_h = int(h * target_size / w)
    
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized
