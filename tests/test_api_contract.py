"""HTTP contract tests with stubbed inference; no weights or external API calls."""
import importlib
import io
import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.errors import ErrorCode, GAICException

# Substitute only the expensive inference boundary while importing the real API.
inference_stub = types.ModuleType("app.aide_inference")
inference_stub.run_inference = Mock()
with patch.dict(sys.modules, {"app.aide_inference": inference_stub}):
    api = importlib.import_module("app.main")


class ApiContractTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)
        self.report = patch.object(api, "generate_report", new_callable=AsyncMock)
        self.report_mock = self.report.start()
        self.report_mock.return_value = ("Test report", None)
        self.addCleanup(self.report.stop)
        buffer = io.BytesIO()
        Image.new("RGB", (16, 16), color="white").save(buffer, format="PNG")
        self.image_bytes = buffer.getvalue()

    def post_image(self):
        return self.client.post("/analyze/image", files={"file": ("test.png", self.image_bytes, "image/png")}, data={"include_heatmap": "false"})

    def test_successful_image_has_model_score(self):
        with patch.object(api, "run_inference", return_value=(0.8, None, 12)):
            response = self.post_image()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 80)
        self.assertEqual(response.json()["errors"], [])

    def test_failed_model_never_returns_a_neutral_score(self):
        for code, status in [(ErrorCode.MODEL_ERROR, 500), (ErrorCode.MODEL_TIMEOUT, 504)]:
            with self.subTest(code=code), patch.object(api, "run_inference", side_effect=GAICException(code)):
                response = self.post_image()
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()["detail"]["error_code"], code)
                self.assertNotIn("score", response.json())
        self.report_mock.assert_not_awaited()

    def test_invalid_image_rejected_before_inference(self):
        with patch.object(api, "run_inference") as inference:
            response = self.client.post("/analyze/image", files={"file": ("bad.png", b"not an image", "image/png")})
            self.assertEqual(response.status_code, 400)
            inference.assert_not_called()

    def test_partial_video_exposes_failed_frame(self):
        frame = np.zeros((16, 16, 3), dtype=np.uint8)
        with patch.object(api, "sample_frames_from_video", return_value=([frame, frame], [0.0, 1.0], 2.0)), patch.object(api, "run_inference", side_effect=[GAICException(ErrorCode.MODEL_ERROR), (0.8, None, 12)]):
            response = self.client.post("/analyze/video", files={"file": ("test.mp4", b"stub", "video/mp4")}, data={"include_heatmap": "false"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 80)
        self.assertEqual(response.json()["key_frame_index"], 1)
        self.assertIn("FRAME_0_MODEL_ERROR", response.json()["errors"])

    def test_all_failed_video_frames_return_error(self):
        frame = np.zeros((16, 16, 3), dtype=np.uint8)
        with patch.object(api, "sample_frames_from_video", return_value=([frame], [0.0], 1.0)), patch.object(api, "run_inference", side_effect=GAICException(ErrorCode.MODEL_ERROR)):
            response = self.client.post("/analyze/video", files={"file": ("test.mp4", b"stub", "video/mp4")})
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("score", response.json())
        self.report_mock.assert_not_awaited()
