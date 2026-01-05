import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon # Add this import
from float import FloatingIcon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set the global application icon (shows in taskbar)
    app.setWindowIcon(QIcon("Bhojam.ico")) 

    app.setQuitOnLastWindowClosed(False)

    icon = FloatingIcon()
    
    # Set the specific widget icon
    icon.setWindowIcon(QIcon("Bhojam.ico")) 
    
    icon.move(100, 300)
    icon.show()

    sys.exit(app.exec())