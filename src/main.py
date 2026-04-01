import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartLeather v1 — Controle de Produção")
        self.resize(800, 480) # Resolução comum em RPI 7" Display

        layout = QVBoxLayout()
        label = QLabel("SmartLeather v1 — Bem-vindo!")
        layout.addWidget(label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() # Para modo fullscreen use window.showFullScreen() no RPI
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
