# Posture Detection Service - Human Pose Estimation using MediaPipe Tasks API
import cv2
import numpy as np
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

# Try to import MediaPipe for pose estimation
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logging.warning("MediaPipe not available, install with: pip install mediapipe")

router = APIRouter(prefix="/api/posture", tags=["posture"])

# Key point indices (MediaPipe pose landmarks)
NOSE = 0
LEFT_EYE_INNER = 1
LEFT_EYE = 2
LEFT_EYE_OUTER = 3
RIGHT_EYE_INNER = 4
RIGHT_EYE = 5
RIGHT_EYE_OUTER = 6
LEFT_EAR = 7
RIGHT_EAR = 8
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12


class PostureResult(BaseModel):
    status: str  # "good" or "bad"
    message: str
    gesture_type: Optional[str] = None  # "shrugging", "head_dropping", "tilting"
    key_points: Optional[List[dict]] = None


class PostureDetector:
    """MediaPipe-based human pose estimation for posture detection"""

    def __init__(self):
        self.detector = None
        self.initialized = False

        # Gesture detection state
        self.w_g1 = 0  # Shrugging counter
        self.w_g2 = 0  # Head dropping counter
        self.w_g3 = 0  # Tilting counter
        self.g_g1 = 0  # Good gesture counter
        self.frame_threshold = 2

    def reset_state(self):
        """Reset detection state counters"""
        self.w_g1 = 0
        self.w_g2 = 0
        self.w_g3 = 0
        self.g_g1 = 0

    def initialize(self):
        """Initialize MediaPipe pose model"""
        if not MEDIAPIPE_AVAILABLE:
            logging.warning("MediaPipe not available, detector will return mock results")
            return False

        try:
            # Create pose landmarker using tasks API
            model_path = 'pose_landmarker.task'
            import os
            if not os.path.exists(model_path):
                logging.error(f"Model file not found: {model_path}")
                return False

            base_options = python.BaseOptions(
                model_asset_path=model_path
            )
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                output_segmentation_masks=False,
                running_mode=vision.RunningMode.IMAGE
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
            self.initialized = True
            self.use_tasks_api = True
            logging.info("MediaPipe posture detector initialized successfully with tasks API")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize MediaPipe pose landmarker: {e}")
            return False

    def detect_gesture(self, key_points: List) -> tuple:
        """Detect posture gesture from key points"""
        if len(key_points) < 7 or None in key_points:
            return "unknown", "无法检测到完整姿态"

        nose = key_points[0]
        l_eye = key_points[1]
        r_eye = key_points[2]
        l_ear = key_points[3]
        r_ear = key_points[4]
        l_shoulder = key_points[5]
        r_shoulder = key_points[6]

        # Calculate metrics
        h_eye = int((l_eye[1] + r_eye[1]) / 2.0)
        h_ear = int((l_ear[1] + r_ear[1]) / 2.0)
        h_shoulder = int((l_shoulder[1] + r_shoulder[1]) / 2)

        dist_n_s = int(abs(h_shoulder - nose[1]))
        dist_ls_rs = int(abs(l_shoulder[0] - r_shoulder[0]))

        eye_slope = float(abs(r_eye[1] - l_eye[1])) / max(float(abs(r_eye[0] - l_eye[0])), 1)
        shoulder_slope = float(abs(r_shoulder[1] - l_shoulder[1])) / max(float(abs(r_shoulder[0] - l_shoulder[0])), 1)

        flag = 0
        fw1, fw2, fw3 = 0, 0, 0

        # Shrugging detection (nose too close to shoulders)
        if dist_n_s < int(dist_ls_rs / 3.0):
            self.w_g1 += 1
            flag = 1
            fw1 = 1

        # Head dropping detection (eyes below ears)
        if h_eye > h_ear:
            self.w_g2 += 1
            flag = 1
            fw2 = 1

        # Tilting detection (asymmetric eyes or shoulders)
        if abs(eye_slope) > 0.2 or abs(shoulder_slope) > 0.2:
            self.w_g3 += 1
            flag = 1
            fw3 = 1

        # Good gesture
        if h_eye < h_ear and flag == 0:
            self.g_g1 += 1

        # Debug: log current state every 10 frames
        if (self.w_g1 + self.w_g2 + self.w_g3 + self.g_g1) % 10 == 0:
            logging.info(f"State: w_g1={self.w_g1}, w_g2={self.w_g2}, w_g3={self.w_g3}, g_g1={self.g_g1}, flag={flag}")

        # Determine result
        if (self.w_g1 > self.frame_threshold or self.w_g2 > self.frame_threshold or
            self.w_g3 > self.frame_threshold) and flag:
            self.g_g1 = 0
            gesture = "Wrong Gesture "
            if fw1:
                gesture += "耸肩 "
            if fw2:
                gesture += "低头 "
            if fw3:
                gesture += "歪头"
            return "bad", gesture.strip()
        else:
            if self.g_g1 > self.frame_threshold and flag == 0:
                self.w_g1 = 0
                self.w_g2 = 0
                self.w_g3 = 0
                return "good", "坐姿良好，请保持"

        return "unknown", "检测中..."

    def detect(self, frame: np.ndarray) -> PostureResult:
        """Detect posture from frame"""
        if not self.initialized:
            return PostureResult(
                status="unknown",
                message="模型未加载，请安装 mediapipe: pip install mediapipe"
            )

        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Use tasks API with mp.Image from root module
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = self.detector.detect(mp_image)

            if not results.pose_landmarks or len(results.pose_landmarks) == 0:
                return PostureResult(
                    status="unknown",
                    message="未检测到人体"
                )

            # Get first detected pose
            landmarks = results.pose_landmarks[0]
            height, width = frame.shape[:2]

            key_points = []
            indices = [NOSE, LEFT_EYE, RIGHT_EYE, LEFT_EAR, RIGHT_EAR, LEFT_SHOULDER, RIGHT_SHOULDER]

            for idx in indices:
                lm = landmarks[idx]
                if hasattr(lm, 'visibility') and lm.visibility > 0.5:
                    key_points.append((
                        int(lm.x * width),
                        int(lm.y * height),
                        lm.visibility if hasattr(lm, 'visibility') else 1.0
                    ))
                else:
                    key_points.append(None)

            # Detect gesture
            status, message = self.detect_gesture(key_points)

            # Format key points for response
            kp_list = None
            if key_points and None not in key_points:
                kp_names = ["nose", "l_eye", "r_eye", "l_ear", "r_ear", "l_shoulder", "r_shoulder"]
                kp_list = [
                    {"name": kp_names[i], "x": int(kp[0]), "y": int(kp[1]), "confidence": float(kp[2])}
                    for i, kp in enumerate(key_points) if kp is not None
                ]

            return PostureResult(
                status=status,
                message=message,
                gesture_type="bad" if status == "bad" else None,
                key_points=kp_list
            )

        except Exception as e:
            logging.error(f"Detection error: {e}")
            return PostureResult(
                status="unknown",
                message=f"检测错误: {str(e)}"
            )

    

# Global detector instance
_detector: Optional[PostureDetector] = None


def get_detector() -> PostureDetector:
    """Get or create detector instance"""
    global _detector
    if _detector is None:
        _detector = PostureDetector()
        _detector.initialize()
    return _detector


@router.post("/detect", response_model=PostureResult)
async def detect_posture_from_file(file: bytes):
    """Detect posture from uploaded image file"""
    try:
        # Decode image
        nparr = np.frombuffer(file, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        detector = get_detector()
        result = detector.detect(frame)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/stream")
async def posture_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time posture detection

    Client sends video frames as base64 encoded JPEG
    Server returns JSON with detection results
    """
    from PIL import Image, ImageDraw, ImageFont
    import json

    await websocket.accept()
    logging.info("WebSocket connected for posture detection")

    detector = get_detector()
    detector.reset_state()

    # Load Chinese font
    font = None
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, 24)
            break
        except:
            continue
    if font is None:
        font = ImageFont.load_default()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Decode base64 frame
                if data.startswith("data:image"):
                    data = data.split(",")[1]

                frame_bytes = base64.b64decode(data)
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is None:
                    await websocket.send_text(json.dumps({"status": "error", "message": "Invalid frame"}, ensure_ascii=False))
                    continue

                # Detect posture
                result = detector.detect(frame)

                # Draw keypoints on frame
                if detector.initialized and result.key_points:
                    for kp in result.key_points:
                        cv2.circle(frame, (kp["x"], kp["y"]), 5, (0, 0, 255), -1)

                    kp_dict = {kp["name"]: (kp["x"], kp["y"]) for kp in result.key_points}
                    connections = [
                        ("nose", "l_eye"), ("nose", "r_eye"),
                        ("l_eye", "l_ear"), ("r_eye", "r_ear"),
                        ("l_shoulder", "r_shoulder"),
                        ("nose", "l_shoulder"), ("nose", "r_shoulder")
                    ]
                    for p1, p2 in connections:
                        if p1 in kp_dict and p2 in kp_dict:
                            cv2.line(frame, kp_dict[p1], kp_dict[p2], (0, 255, 0), 2)

                # Draw Chinese text using PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                draw = ImageDraw.Draw(pil_image)

                text = result.message
                color = (0, 200, 0) if result.status == "good" else (200, 0, 0)

                try:
                    bbox = draw.textbbox((10, 10), text, font=font)
                    draw.rectangle([bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5], fill=(0, 0, 0))
                except:
                    draw.rectangle([5, 5, 300, 40], fill=(0, 0, 0))

                draw.text((10, 10), text, font=font, fill=color)

                # Convert back to OpenCV format
                frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                result_frame_b64 = base64.b64encode(buffer).decode('utf-8')

                response_data = {
                    "status": result.status,
                    "message": result.message,
                    "gesture_type": result.gesture_type,
                    "key_points": result.key_points,
                    "frame": result_frame_b64
                }
                await websocket.send_text(json.dumps(response_data, ensure_ascii=False))

            except Exception as e:
                logging.error(f"Frame processing error: {e}")
                try:
                    await websocket.send_text(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
                except:
                    pass

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    detector = get_detector()
    return {
        "status": "ok",
        "mediapipe_available": MEDIAPIPE_AVAILABLE,
        "model_loaded": detector.initialized
    }
