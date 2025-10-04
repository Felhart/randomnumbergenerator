import sys
import os
import random
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt, QTimer
import pygame


# resource_path fonksiyonu ve diğer başlangıç kısımları aynı kalıyor...
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.generated_numbers = set()
        self.init_sound()
        self.init_ui()
        self.apply_styles()

    def init_sound(self):
        # Bu fonksiyon aynı kalıyor...
        pygame.mixer.init()
        sound_effect_path = resource_path(os.path.join("assets", "sounds", "generate_sound.wav"))
        try:
            self.reveal_sound = pygame.mixer.Sound(sound_effect_path)
        except pygame.error:
            print(f"Uyarı: Efekt sesi bulunamadı: {sound_effect_path}")
            self.reveal_sound = None
        music_path = resource_path(os.path.join("assets", "sounds", "superhero.mp3"))
        try:
            pygame.mixer.music.load(music_path)
        except pygame.error:
            print(f"Uyarı: Müzik dosyası bulunamadı: {music_path}")

    def init_ui(self):
        # Bu fonksiyon da tam ekran ayarlarıyla aynı kalıyor...
        self.setWindowTitle("Rastgele Sayı Üretici")
        font_path = resource_path(os.path.join("assets", "fonts", "DS-DIGI.TTF"))
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id < 0:
            self.digital_font_family = "Arial"
        else:
            self.digital_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(25)
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
        self.generate_button.clicked.connect(self.start_generation_process)
        self.reset_button = QPushButton("Sıfırla")
        self.reset_button.clicked.connect(self.reset_generator)
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.reset_button)
        self.result_container = QWidget()
        self.result_container.setObjectName("resultContainer")
        result_layout = QVBoxLayout()
        self.result_label = QLabel("?")
        self.result_label.setAlignment(Qt.AlignCenter)
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
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)
        content_layout.addWidget(self.title_label)
        content_layout.addLayout(input_layout)
        content_layout.addLayout(button_layout)
        content_layout.addWidget(self.result_container, 1)
        content_layout.addWidget(self.status_label)
        main_layout.addStretch(1)
        main_layout.addLayout(content_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def start_generation_process(self):
        # Bu fonksiyona pencerenin orijinal pozisyonunu kaydetmeyi ekliyoruz.
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

        # --- YENİ: Pencerenin pozisyonunu kaydediyoruz ---
        self.original_window_pos = self.pos()
        self.original_label_pos = self.result_label.pos()

        pygame.mixer.music.play()
        self.main_sequence_timer.start(40)  # Animasyon saniyede 25 kare

    def update_main_sequence(self):
        """Tüm animasyon sürecini yöneten, 3 aşamalı yeni fonksiyon."""

        # --- DEĞİŞTİ: Animasyon süresini ve aşamalarını tanımlıyoruz ---
        BUILDUP_FRAMES = 240  # ~9.6 saniye slot makinesi
        REVEAL_FRAME = BUILDUP_FRAMES
        CRAZY_SHAKE_DURATION = 125  # ~5 saniye manyak titreme

        # AŞAMA 1: Yükseliş (Slot makinesi efekti)
        if self.sequence_counter < BUILDUP_FRAMES:
            display_number = random.randint(self.min_val, self.max_val)
            self.result_label.setText(str(display_number))
            # Bu aşamada sadece sayı titriyor
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            self.result_label.move(self.original_label_pos.x() + dx, self.original_label_pos.y() + dy)

        # AŞAMA 2: Açıklanma (Sadece 1 kare sürer)
        elif self.sequence_counter == REVEAL_FRAME:
            self.result_label.move(self.original_label_pos)  # Sayıyı orijinal yerine koy
            self.result_label.setText(str(self.final_number))  # GERÇEK SAYIYI GÖSTER
            self.generated_numbers.add(self.final_number)
            if self.reveal_sound:
                self.reveal_sound.play()

        # AŞAMA 3: Kopuş (Manyak titreme)
        elif self.sequence_counter < REVEAL_FRAME + CRAZY_SHAKE_DURATION:
            # --- YENİ: TÜM PENCEREYİ TİTRETİYORUZ ---
            # Titreşim genliğini artırarak daha "manyak" bir his veriyoruz
            dx = random.randint(-15, 15)
            dy = random.randint(-15, 15)
            self.move(self.original_window_pos.x() + dx, self.original_window_pos.y() + dy)

        # ANİMASYON BİTTİ
        else:
            self.main_sequence_timer.stop()
            # --- ÇOK ÖNEMLİ: Pencereyi orijinal pozisyonuna geri getir ---
            self.move(self.original_window_pos)

            total_possible = (self.max_val - self.min_val) + 1
            generated_count = len(self.generated_numbers)
            self.status_label.setText(f"Kazanan: {self.final_number}! ({generated_count}/{total_possible})")
            self.generate_button.setEnabled(True)
            self.reset_button.setEnabled(True)

        self.sequence_counter += 1

    def reset_generator(self):
        # Sıfırlama sırasında müziği de durduralım
        if not self.generate_button.isEnabled(): return

        pygame.mixer.music.stop()  # Çalan müziği durdur

        self.generated_numbers.clear()
        self.result_label.setText("?")
        self.min_input.setText("1")
        self.max_input.setText("100")
        self.status_label.setText("Sistem sıfırlandı. Başlamaya hazır.")
        QMessageBox.information(self, "Sıfırlandı", "Üretilen sayılar listesi temizlendi.")

    def apply_styles(self):
        # Stil kodları aynı kalıyor...
        style_sheet = """
            MainWindow { background-color: #1e1e2f; } #titleLabel { color: #c9c9ff; font-size: 48px; font-weight: bold; letter-spacing: 3px; } QLineEdit { background-color: #2a2a40; color: #f0f0f0; border: 2px solid #4a4a6a; border-radius: 12px; padding: 15px; font-size: 24px; } QLineEdit:focus { border-color: #8a8ac0; } QPushButton { color: white; font-size: 28px; font-weight: bold; border: none; border-radius: 18px; padding: 20px; } QPushButton:disabled { background-color: #555; color: #999; } #generateButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8e44ad, stop:1 #3498db); } #generateButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9b59b6, stop:1 #5dade2); } #generateButton:pressed { background-color: #8e44ad; } #resetButton { background-color: #4a4a6a; } #resetButton:hover { background-color: #5a5a7a; } #resetButton:pressed { background-color: #3a3a5a; } #resultContainer { background-color: #10101a; border: 3px solid #00d0ff; border-radius: 25px; } #resultLabel { color: #00d0ff; font-size: 250px; } #statusLabel { color: #7a7a9a; font-size: 20px; }
        """
        self.generate_button.setObjectName("generateButton")
        self.reset_button.setObjectName("resetButton")
        self.setStyleSheet(style_sheet)