"""Hi5 Portfolio Desktop App - Main entry point"""
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Hi5 Portfolio Manager")
    app.setOrganizationName("Hi5")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
