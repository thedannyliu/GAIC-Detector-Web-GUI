"""
Backward compatibility layer for models module.

This module re-exports the AIDE model functionality to maintain
compatibility with any existing imports.
"""

from app.aide_model import (
    AIDeDetector,
    AIDeInference,
    get_aide_model,
    run_inference
)

__all__ = [
    'AIDeDetector',
    'AIDeInference',
    'get_aide_model',
    'run_inference'
]
