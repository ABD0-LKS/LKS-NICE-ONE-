import cv2
import pyzbar.pyzbar as pyzbar
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtMultimedia import QSound
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMessageBox
from typing import Optional, Tuple

class BarcodeScanner(QObject):
    """Handles barcode scanning functionality"""
    barcode_scanned = pyqtSignal(str)
    scan_status = pyqtSignal(str, str)  # message, color
    unknown_barcode = pyqtSignal(str)
    frame_ready = pyqtSignal(QImage)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.capture: Optional[cv2.VideoCapture] = None
        self.scanning = False
        self.device_id: int = 0
        self.known_formats = {'EAN13', 'EAN8', 'UPCA', 'UPCE', 'CODE128', 'CODE39', 'QRCODE'}
        # Debouncing to avoid repeating the same code too fast
        self._last_seen_code: Optional[str] = None
        self._last_seen_at: float = 0.0
        self._min_interval_sec: float = 0.8

        # Optional sounds: fall back to no-files mode
        self._has_sound = False
        try:
            from PyQt5.QtMultimedia import QSound
            self.success_sound = QSound("sounds/success.wav")
            self.error_sound = QSound("sounds/error.wav")
            self._has_sound = True
        except Exception:
            self.success_sound = None
            self.error_sound = None
        
    def _play_success(self):
        try:
            if self._has_sound and self.success_sound:
                self.success_sound.play()
            else:
                # Fallback to a system beep if sound files are missing
                from PyQt5.QtWidgets import QApplication
                QApplication.beep()
        except Exception:
            pass

    def _play_error(self):
        try:
            if self._has_sound and self.error_sound:
                self.error_sound.play()
            else:
                from PyQt5.QtWidgets import QApplication
                QApplication.beep()
        except Exception:
            pass
    
    def start_scanning(self, device_id=0):
        """Start the barcode scanning process"""
        try:
            self.capture = cv2.VideoCapture(device_id)
            if not self.capture.isOpened():
                raise Exception("Could not open video device")
                
            self.scanning = True
            self.scan_status.emit("Camera initialized", "#17a2b8")
            self.process_frames()
            
        except Exception as e:
            self.scan_status.emit(f"Camera error: {str(e)}", "#dc3545")
            self._play_error()
    
    def stop_scanning(self):
        """Stop the barcode scanning process"""
        self.scanning = False
        if self.capture:
            self.capture.release()
        self.scan_status.emit("Scanner stopped", "#6c757d")
    
    def process_frames(self):
        """Process video frames for barcode detection"""
        while self.scanning:
            ret, frame = self.capture.read()
            if not ret:
                self.scan_status.emit("Failed to capture frame", "#dc3545")
                continue
                
            # Mirror view for user friendliness
            frame = cv2.flip(frame, 1)

            # Emit preview frame
            qimg = self._to_qimage(frame)
            if qimg is not None:
                self.frame_ready.emit(qimg)

            # Convert to grayscale for better detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect barcodes
            barcodes = pyzbar.decode(gray)
            
            now = time.time()
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8", errors="ignore")
                barcode_type = (barcode.type or "").upper()
                
                # Debounce: ignore if same code too soon
                if barcode_data and (barcode_data != self._last_seen_code or (now - self._last_seen_at) >= self._min_interval_sec):
                    self._last_seen_code = barcode_data
                    self._last_seen_at = now

                    if barcode_type in self.known_formats or barcode_type.replace("-", "") in self.known_formats:
                        self.barcode_scanned.emit(barcode_data)
                        self._play_success()
                        self.scan_status.emit(f"Scanned: {barcode_type}", "#28a745")
                    else:
                        self.unknown_barcode.emit(barcode_data)
                        self._play_error()
                        self.scan_status.emit(f"Unknown format: {barcode_type or 'UNKNOWN'}", "#ffc107")
            
            # Small delay to prevent high CPU usage
            time.sleep(0.02)

    def _release_camera(self):
        if self.capture:
            try:
                self.capture.release()
            except Exception:
                pass
        self.capture = None

    def _to_qimage(self, frame) -> Optional[QImage]:
        try:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            # Convert BGR to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            return qimg.copy()
        except Exception:
            return None

    def log_unknown_barcode(self, barcode: str):
        """Append unknown barcode to a local log file."""
        try:
            with open("unknown_barcodes.log", "a", encoding="utf-8") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{ts} - {barcode}\n")
        except Exception:
            # Fail silently to avoid crashing the UI
            pass
