import sys
import subprocess
import time
import win32gui
import win32con
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer

class UsableVDE(QWidget):
    def __init__(self):
        super().__init__()
        self.open_windows = {} # Tallennetaan käynnissä olevat ikkunat {Nimi: HWND-tunnus}
        self.initUI()
        
        # Ajastin, joka päivittää avoinna olevien ohjelmien tilan taustalla
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_window_tracker)
        self.timer.start(1000) # Päivitetään sekunnin välein

    def initUI(self):
        # Tehdään työpöydästä koko näytön kokoinen taustakerros
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #1e1e2e;") # Tumma moderni tausta

        # Pääasettelu (Layout)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Työpöytäalue (Yläosa)
        desktop_area = QWidget()
        desktop_layout = QHBoxLayout()
        desktop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Painike 1: Avaa täysin käytettävä selain
        btn_edge = QPushButton("Käynnistä selain", self)
        btn_edge.setStyleSheet("background-color: #313244; color: white; padding: 20px; font-size: 18px; border-radius: 10px; min-width: 200px;")
        btn_edge.clicked.connect(lambda: self.launch_program("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe", "Edge"))
        desktop_layout.addWidget(btn_edge)

        # Painike 2: Avaa Notepad testiä varten
        btn_notepad = QPushButton("Avaa Tekstieditori", self)
        btn_notepad.setStyleSheet("background-color: #313244; color: white; padding: 20px; font-size: 18px; border-radius: 10px; min-width: 200px;")
        btn_notepad.clicked.connect(lambda: self.launch_program("notepad.exe", "Notepad"))
        desktop_layout.addWidget(btn_notepad)

        desktop_area.setLayout(desktop_layout)
        main_layout.addWidget(desktop_area, stretch=9)

        # 2. Oma Tehtäväpalkki (Alaosa)
        self.taskbar = QWidget()
        self.taskbar.setStyleSheet("background-color: #11111b; border-top: 2px solid #313244;")
        self.taskbar_layout = QHBoxLayout()
        self.taskbar_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Lisätään pieni logo tai teksti palkkiin
        lbl = QLabel(" VDE OS | ", self)
        lbl.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 14px; font-family: Arial;")
        self.taskbar_layout.addWidget(lbl)
        
        self.taskbar.setLayout(self.taskbar_layout)
        main_layout.addWidget(self.taskbar, stretch=1)

        self.setLayout(main_layout)

    def launch_program(self, path, internal_name):
        """Käynnistää ohjelman ja tuo sen näkyviin"""
        subprocess.Popen([path])
        # Ohjelma aukeaa normaalisti Windowsissa ja on täysin käytettävissä.
        # Seuraavaksi järjestelmä alkaa seurata sen ikkunaa, jotta sitä voidaan hallita.

    def update_window_tracker(self):
        """Etsii avoimet ikkunat ja luo niille painikkeet omaan tehtäväpalkkiin"""
        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # Suodatetaan vain oikeat sovellusikkunat (esim. Edge tai Notepad)
                if "Notepad" in title or "Edge" in title or "Chrome" in title:
                    if hwnd not in self.open_windows.values():
                        self.create_taskbar_button(title, hwnd)
        
        win32gui.EnumWindows(enum_windows_callback, None)

    def create_taskbar_button(self, title, hwnd):
        """Luo alapalkkiin painikkeen, josta ohjelman saa tuotua etualalle"""
        short_title = title[:15] + "..." if len(title) > 15 else title
        btn = QPushButton(short_title)
        btn.setStyleSheet("background-color: #45475a; color: white; padding: 5px 15px; border-radius: 5px; font-size: 12px;")
        
        # Kun painiketta klikataan, pakotetaan kyseinen ohjelma etualalle (Focus)
        btn.clicked.connect(lambda: self.bring_to_foreground(hwnd))
        
        self.taskbar_layout.addWidget(btn)
        self.open_windows[title] = hwnd

    def bring_to_foreground(self, hwnd):
        """Nostaa valitun ohjelman ikkunan muiden päälle käytettäväksi"""
        if win32gui.IsWindow(hwnd):
            # Jos ikkuna on minimoitu, palautetaan se
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Tuodaan ikkuna päällimmäiseksi
            win32gui.SetForegroundWindow(hwnd)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UsableVDE()
    sys.exit(app.exec())
