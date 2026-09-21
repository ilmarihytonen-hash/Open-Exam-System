import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

# CONFIGURATION: Enforce trailing slash to align with modern web standard definitions
TARGET_URL = "https://www.wikipedia.org/" 

class SinglePageBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Dedicated Application")
        self.resize(1024, 768)

        # 1. Establish Secure Sandbox Profile
        self.setup_security_profile()

        # 2. Main Web View Component
        self.browser = QWebEngineView()
        self.secure_page = QWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.secure_page)
        
        # 3. Restrict Navigation via Overridden Event Filtering
        self.secure_page.acceptNavigationRequest = self.handle_navigation_request

        # Load the designated URL
        self.browser.setUrl(QUrl(TARGET_URL))

        # 4. Clean UI Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def setup_security_profile(self):
        """Configures sandboxing parameters using proper PyQt6 naming conventions."""
        self.profile = QWebEngineProfile("", self) # Incognito / temporary session
        
        settings = self.profile.settings()
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, False)
        
        # Fixed lowercase variant targeting newer PyQt6 builds
        settings.setAttribute(settings.WebAttribute.JavascriptCanOpenWindows, False) 

    def handle_navigation_request(self, qurl, nav_type, is_main_frame):
        """Security guard: Only allows subpages inside the target domain to load."""
        requested_url = qurl.toString()
        
        # Checking with startswith allows navigation inside sub-directories 
        # (e.g., https://wikipedia.org) while blocking outside sites.
        if requested_url.startswith(TARGET_URL):
            return True
            
        print(f"🚫 Blocked unauthorized navigation attempt to: {requested_url}")
        return False

    def closeEvent(self, event):
        """Explicitly tears down engine processes to prevent memory release warnings."""
        self.browser.setPage(None)
        self.secure_page.deleteLater()
        self.browser.deleteLater()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SinglePageBrowser()
    window.show()
    sys.exit(app.exec())
