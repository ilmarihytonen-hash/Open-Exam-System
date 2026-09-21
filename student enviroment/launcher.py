import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QBrush

# Varatila-asetukset silti olemassa kaatumisen estämiseksi
DEFAULT_CONFIG = {
    "WINDOW_WIDTH": 600,
    "WINDOW_HEIGHT": 400,
    "ACCENT_COLOR": "#89b4fa",
    "TEXT_COLOR_MAIN": "#ffffff",
    "TEXT_COLOR_SUB": "#a6adc8",
    "BACKGROUND_IMAGE": "",
    "FALLBACK_BG_COLOR": "#1e1e2e",
    "BRAND_TITLE": "PYTHON ALUSTA",
    "SUB_TITLE": "SUOJATTU TYÖTILA",
    "STAY_ON_TOP": True,
    "SHOW_PROGRESS_BAR": True,
    "ANIMATION_SPEED_MS": 30,
    "LOADING_STEPS": [
        [30, "Ladataan..."],
        [100, "Valmis..."]
    ]
}

def load_ui_configuration():
    """Lukee asetukset suoraan uiconfig.json tiedostosta."""
    # MUUTETTU: Tiedoston nimeksi vaihdettu uiconfig.json
    config_path = os.path.join(os.path.dirname(__file__), "uiconfig.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"⚠️ Virhe uiconfig.json tiedoston lukemisessa: {e}. Käytetään oletuksia.")
    else:
        print("⚠️ Tiedostoa uiconfig.json ei löytynyt! Käytetään koodin sisäisiä oletuksia.")
    return DEFAULT_CONFIG

# Ladataan asetukset globaaliin muuttujaan korjatulla nimellä
CONFIG = load_ui_configuration()

try:
    from secure_app import SinglePageBrowser
except ImportError:
    from PyQt6.QtWidgets import QMainWindow
    class SinglePageBrowser(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Pääsovellus (Varatila)")
            self.resize(1024, 768)

class ConfigurableSplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        window_flags = Qt.WindowType.FramelessWindowHint
        if CONFIG.get("STAY_ON_TOP", True):
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        
        self.resize(CONFIG.get("WINDOW_WIDTH", 600), CONFIG.get("WINDOW_HEIGHT", 400))
        
        self.current_step_index = 0
        self.progress_value = 0
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loading_progress)
        self.timer.start(CONFIG.get("ANIMATION_SPEED_MS", 30))

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 50, 40, 40)
        
        bg_image = CONFIG.get("BACKGROUND_IMAGE", "")
        if bg_image and os.path.exists(bg_image):
            pixmap = QPixmap(bg_image).scaled(
                self.size(), 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            )
            palette = QPalette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        else:
            self.setStyleSheet(f"background-color: {CONFIG.get('FALLBACK_BG_COLOR', '#1e1e2e')};")

        brand_label = QLabel(CONFIG.get("BRAND_TITLE", "APP"))
        brand_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        brand_label.setStyleSheet(f"color: {CONFIG.get('ACCENT_COLOR', '#89b4fa')}; background: transparent; letter-spacing: 2px;")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_label = QLabel(CONFIG.get("SUB_TITLE", ""))
        sub_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        sub_label.setStyleSheet(f"color: {CONFIG.get('TEXT_COLOR_SUB', '#a6adc8')}; background: transparent;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Alustetaan...")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet(f"color: {CONFIG.get('TEXT_COLOR_MAIN', '#ffffff')}; background: transparent;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {CONFIG.get('ACCENT_COLOR', '#89b4fa')};
                border-radius: 4px;
            }}
        """)
        
        if not CONFIG.get("SHOW_PROGRESS_BAR", True):
            self.progress_bar.hide()

        layout.addWidget(brand_label)
        layout.addWidget(sub_label)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.center_on_screen()

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_loading_progress(self):
        steps = CONFIG.get("LOADING_STEPS", DEFAULT_CONFIG["LOADING_STEPS"])
        
        if self.progress_value < 100:
            self.progress_value += 1
            self.progress_bar.setValue(self.progress_value)
            
            target_pct, message = steps[self.current_step_index]
            self.status_label.setText(message)
            
            if self.progress_value >= target_pct and self.current_step_index < len(steps) - 1:
                self.current_step_index += 1
        else:
            self.timer.stop()
            self.launch_main_application()

    def launch_main_application(self):
        self.main_window = SinglePageBrowser()
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = ConfigurableSplashScreen()
    splash.show()
    sys.exit(app.exec())
