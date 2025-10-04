import sys
import os
import random
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QLineEdit,QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt, QTimer
import pygame

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller geçici bir klasör oluşturur ve yolu _MEIPASS içinde saklar.
        base_path = sys._MEIPASS
    except Exception:
        # PyInstaller ile çalışmıyorsa, normal dosya yolunu kullan.
        # Bu kod ui klasöründe olduğu için, ana dizine (SAYI_URETICI) çıkmalıyız.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)
# -----------------------------------------------------------------


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.generated_numbers = set()

        self.init_sound()
        self.init_ui()
        self.apply_styles()

    def init_sound(self):
        """Ses motorunu başlatır ve ses dosyalarını yükler."""
        pygame.mixer.init()

        # --- DEĞİŞTİ: resource_path fonksiyonunu kullanıyoruz ---
        sound_effect_path = resource_path(os.path.join("assets", "sounds", "generate_sound.wav"))
        try:
            self.reveal_sound = pygame.mixer.Sound(sound_effect_path)
        except pygame.error:
            print(f"Uyarı: Efekt sesi bulunamadı: {sound_effect_path}")
            self.reveal_sound = None

        # --- DEĞİŞTİ: resource_path fonksiyonunu kullanıyoruz ---
        music_path = resource_path(os.path.join("assets", "sounds", "drum_roll_effect.mp3"))
        try:
            pygame.mixer.music.load(music_path)
        except pygame.error:
            print(f"Uyarı: Müzik dosyası bulunamadı: {music_path}")

    def init_ui(self):
        """Arayüz elemanlarını oluşturur ve yerleştirir."""
        self.setWindowTitle("Rastgele Sayı Üretici")

        # --- DEĞİŞİKLİK 1: SABİT BOYUTU KALDIRIYORUZ ---
        # self.setFixedSize(450, 550) # Bu satırı siliyoruz veya yorum satırı yapıyoruz.

        # Dijital fontu yükle... (Bu kısım aynı)
        font_path = os.path.join(BASE_DIR, "assets", "fonts", "DS-DIGI.TTF")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id < 0:
            self.digital_font_family = "Arial"
        else:
            self.digital_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        # Ana layout...
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(25)

        # Diğer elemanlar... (Bu kısımlar aynı)
        self.title_label = QLabel("RASTGELE SAYI ÜRETİCİ")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("titleLabel")

        input_layout = QHBoxLayout()
        self.min_input = QLineEdit("1")
        self.max_input = QLineEdit("100")
        input_layout.addWidget(self.min_input)
        input_layout.addWidget(self.max_input)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("SAYI ÜRET")
        self.generate_button.setCursor(Qt.PointingHandCursor)
        self.generate_button.clicked.connect(self.start_generation_process)

        self.reset_button = QPushButton("Sıfırla")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self.reset_generator)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.reset_button)

        self.result_container = QWidget()
        self.result_container.setObjectName("resultContainer")
        result_layout = QVBoxLayout()
        self.result_label = QLabel("?")
        self.result_label.setAlignment(Qt.AlignCenter)
        # Font boyutunu büyütüyoruz (apply_styles içinde yapacağız)
        self.result_label.setFont(QFont(self.digital_font_family, 120))
        self.result_label.setObjectName("resultLabel")
        result_layout.addWidget(self.result_label)
        self.result_container.setLayout(result_layout)

        self.status_label = QLabel("Başlamak için butona basın.")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("statusLabel")

        self.main_sequence_timer = QTimer(self)
        self.main_sequence_timer.timeout.connect(self.update_main_sequence)
        self.sequence_counter = 0

        # --- DEĞİŞİKLİK 2: ARAYÜZÜ ORTALAMAK İÇİN BOŞLUK EKLEME ---
        # Bütün elemanları bir alt-layout'a koyalım
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)
        content_layout.addWidget(self.title_label)
        content_layout.addLayout(input_layout)
        content_layout.addLayout(button_layout)
        content_layout.addWidget(self.result_container, 1)  # 1 ile daha fazla yer kaplamasını sağla
        content_layout.addWidget(self.status_label)

        # Şimdi asıl ana layout'a üstten ve alttan esnek boşluk ekliyoruz
        main_layout.addStretch(1)  # Üstteki boşluk
        main_layout.addLayout(content_layout)  # Ortadaki içeriğimiz
        main_layout.addStretch(1)  # Alttaki boşluk

        self.setLayout(main_layout)

    def start_generation_process(self):
        # Bu fonksiyon değişmedi
        try:
            self.min_val = int(self.min_input.text())
            self.max_val = int(self.max_input.text())
        except ValueError:
            QMessageBox.warning(self, "Hatalı Giriş", "Lütfen sadece sayısal değerler girin.")
            return

        if self.min_val > self.max_val:
            self.min_val, self.max_val = self.max_val, self.min_val
            self.min_input.setText(str(self.min_val))
            self.max_input.setText(str(self.max_val))

        possible_numbers_count = (self.max_val - self.min_val) + 1
        if len(self.generated_numbers) >= possible_numbers_count:
            QMessageBox.information(self, "Tamamlandı", "Bu aralıktaki tüm sayılar zaten üretildi!")
            return

        while True:
            self.final_number = random.randint(self.min_val, self.max_val)
            if self.final_number not in self.generated_numbers:
                break

        self.sequence_counter = 0
        self.generate_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.status_label.setText("Sayı seçiliyor...")
        self.original_pos = self.result_label.pos()
        pygame.mixer.music.play()
        self.main_sequence_timer.start(40)

    def update_main_sequence(self):
        # Bu fonksiyon değişmedi
        if self.sequence_counter < 80:
            display_number = random.randint(self.min_val, self.max_val)
            self.result_label.setText(str(display_number))
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            self.result_label.move(self.original_pos.x() + dx, self.original_pos.y() + dy)
            self.sequence_counter += 1
        else:
            self.main_sequence_timer.stop()
            ##pygame.mixer.music.stop()
            self.result_label.move(self.original_pos)
            self.result_label.setText(str(self.final_number))
            self.generated_numbers.add(self.final_number)
            if self.reveal_sound:
                self.reveal_sound.play()
            total_possible = (self.max_val - self.min_val) + 1
            generated_count = len(self.generated_numbers)
            self.status_label.setText(f"Kazanan: {self.final_number}! ({generated_count}/{total_possible})")
            self.generate_button.setEnabled(True)
            self.reset_button.setEnabled(True)

    def reset_generator(self):
        # Bu fonksiyon değişmedi
        if not self.generate_button.isEnabled(): return
        self.generated_numbers.clear()
        self.result_label.setText("?")
        self.min_input.setText("1")
        self.max_input.setText("100")
        self.status_label.setText("Sistem sıfırlandı. Başlamaya hazır.")
        QMessageBox.information(self, "Sıfırlandı", "Üretilen sayılar listesi temizlendi.")

    def apply_styles(self):
        """Uygulamanın şık görünmesi için QSS stillerini uygular."""
        # --- DEĞİŞİKLİK 3: FONT BOYUTLARINI BÜYÜTME ---
        style_sheet = """
            MainWindow { background-color: #1e1e2f; }
            #titleLabel { color: #c9c9ff; font-size: 48px; font-weight: bold; letter-spacing: 3px; }
            QLineEdit { background-color: #2a2a40; color: #f0f0f0; border: 2px solid #4a4a6a; border-radius: 12px; padding: 15px; font-size: 24px; }
            QLineEdit:focus { border-color: #8a8ac0; }
            QPushButton { color: white; font-size: 28px; font-weight: bold; border: none; border-radius: 18px; padding: 20px; }
            QPushButton:disabled { background-color: #555; color: #999; }
            #generateButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8e44ad, stop:1 #3498db); }
            #generateButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9b59b6, stop:1 #5dade2); }
            #generateButton:pressed { background-color: #8e44ad; }
            #resetButton { background-color: #4a4a6a; }
            #resetButton:hover { background-color: #5a5a7a; }
            #resetButton:pressed { background-color: #3a3a5a; }
            #resultContainer { background-color: #10101a; border: 3px solid #00d0ff; border-radius: 25px; }
            #resultLabel { color: #00d0ff; font-size: 250px; } /* En büyük değişiklik burada */
            #statusLabel { color: #7a7a9a; font-size: 20px; }
        """
        # Butonlara ayrı stil verebilmek için ID atayalım
        self.generate_button.setObjectName("generateButton")

        self.setStyleSheet(style_sheet)