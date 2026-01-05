import sys
import tempfile
import cv2
import os
import easyocr
import ollama
from PySide6.QtCore import QObject, Slot, Signal, QThread, QTimer, Qt
from PySide6.QtGui import QImage, QPixmap, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, 
    QPushButton, QFileDialog, QHBoxLayout
)

# ==========================================================
# PROMPT BUILDER
# ==========================================================
def build_prompt(extracted_text: str) -> str:
    return f"""
Act as a direct and blunt Food Label Expert. Analyze the food label provided below and give me a short, scannable report using only bullet points. Use simple language that a non-expert can understand.

Follow this exact structure:

Health Rating: Provide a rating (Good / Okay / Not healthy) and a Score out of 10.

The Big 3 (Levels): List Sugar, Salt, and Fat as (Low / Medium / High).

Health Impact: Tell me directly what diseases or body issues this can cause (e.g., 'Causes belly fat,' 'Spikes blood sugar,' 'Hard on heart').

Suitability: Is it good for Diabetes? Is it good for Kids? (Answer: Yes/No/Moderation).

Allergens: List them clearly.

Who should avoid it: Be specific.

The Bottom Line (Buying Advice): Tell me directly: Should I buy this? If yes, exactly how many times per week is safe to eat?

One Simple Tip: A 'Golden Rule' to make this food safer or healthier.

Food label text:
{extracted_text}
"""

# ==========================================================
# CAMERA DIALOG (LIVE FEED)
# ==========================================================
class CameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Food Label")
        self.setFixedSize(640, 560)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        
        self.video_label = QLabel("Initializing Camera...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.video_label)
        
        controls = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.setFixedHeight(40)
        self.capture_btn.clicked.connect(self.capture)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        
        controls.addWidget(self.cancel_btn)
        controls.addWidget(self.capture_btn)
        layout.addLayout(controls)
        
        self.cap = cv2.VideoCapture(0)
        self.final_frame = None
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Prepare image for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            qt_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_img).scaled(640, 480, Qt.KeepAspectRatio))
            self.last_frame = frame

    def capture(self):
        self.final_frame = self.last_frame
        self.accept()

    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        super().closeEvent(event)

# ==========================================================
# WORKER (PREVENTS UI FREEZE)
# ==========================================
class AnalysisWorker(QObject):
    finished = Signal(str)

    def __init__(self, reader, image_path):
        super().__init__()
        self.reader = reader
        self.image_path = image_path

    @Slot()
    def run(self):
        try:
            # 1. OCR
            print("[Worker] Running OCR...")
            results = self.reader.readtext(self.image_path, detail=0)
            text = "\n".join(results)

            if not text.strip():
                self.finished.emit("No text detected. Try a clearer photo.")
                return

            # 2. AI Analysis
            print("[Worker] Calling Ollama...")
            response = ollama.chat(
                model="gemma3:1b",
                messages=[{"role": "user", "content": build_prompt(text)}]
            )
            ans = response.get("message", {}).get("content", "").strip()
            self.finished.emit(ans or "AI failed to respond.")
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

# ==========================================================
# MAIN BRIDGE
# ==========================================
class CopilotBridge(QObject):
    resultReady = Signal(str)
    loading = Signal(bool)

    def __init__(self):
        super().__init__()
        try:
            # 🔥 CHANGED: Set gpu=True to use NVIDIA CUDA
            self.reader = easyocr.Reader(['en'], gpu=True)
            print("[Bridge] EasyOCR initialized with GPU support.")
        except Exception as e:
            print(f"[Bridge] GPU initialization failed, falling back to CPU. Error: {e}")
            self.reader = easyocr.Reader(['en'], gpu=False)

        self._busy = False
        self._thread = None
        self._worker = None

    @Slot()
    def capture_camera(self):
        if self._busy: return
        
        # FIX 2: Find the active window to use as parent so it stays in front
        parent_window = QApplication.activeWindow()
        cam = CameraDialog(parent_window)
        
        if cam.exec() == QDialog.Accepted and cam.final_frame is not None:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            cv2.imwrite(tmp.name, cam.final_frame)
            self._start_processing(tmp.name)
        else:
            # Just reset busy state if cancelled, don't close anything
            self._busy = False
            self.loading.emit(False)

    @Slot()
    def upload_image(self):
        if self._busy: return
        
        # FIX 3: Use the active window as parent for the File Dialog
        parent_window = QApplication.activeWindow()
        path, _ = QFileDialog.getOpenFileName(
            parent_window, 
            "Select Label", 
            "", 
            "Images (*.png *.jpg *.jpeg)"
        )
        
        if path:
            self._start_processing(path)
        else:
            # Reset state if user cancelled the file picker
            self._busy = False
            self.loading.emit(False)

    @Slot()
    def scan_window(self):
        if self._busy: return
        screen = QGuiApplication.primaryScreen()
        pixmap = screen.grabWindow(0)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        pixmap.save(tmp.name, "PNG")
        self._start_processing(tmp.name)

    def _start_processing(self, path):
        self._busy = True
        self.loading.emit(True)

        self._thread = QThread()
        self._worker = AnalysisWorker(self.reader, path)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_finished)
        
        # Cleanup chain
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._worker.deleteLater()

        self._thread.start()

    @Slot(str)
    def _on_finished(self, result):
        self._busy = False
        self.loading.emit(False)
        self.resultReady.emit(result)