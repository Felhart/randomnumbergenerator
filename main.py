import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == '__main__':
    # Uygulama nesnkesini oluştur
    app = QApplication(sys.argv)

    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()

    # Uygulamanın döngüsünü başlat ve çıkış kodunu bekle
    sys.exit(app.exec_())