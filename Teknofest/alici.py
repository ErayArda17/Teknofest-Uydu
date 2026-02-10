import cv2
import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage

# --- AYARLAR ---
# UDP üzerinden yayın yapılıyorsa genelde format: "udp://IP:PORT"
# Eğer bir Gstreamer pipeline ise buraya o pipeline string'i gelir.
VIDEO_URL = "udp://192.168.1.124:5600"


class VideoAlici(QThread):
    # UI tarafına her kareyi (frame) QImage olarak fırlatır
    yeni_kare = Signal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calisiyor = True
        self.cap = None
        self.out = None  # VideoWriter nesnesi

        # Kayıt Dosyası İsmi (Zaman Damgalı)
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.kayit_dosyasi = f"VideoLog_{zaman}.avi"
        self.kayit_aktif = False

    def run(self):
        # 1. BAĞLANTIYI BAŞLAT
        # cv2.CAP_FFMPEG arka ucunu zorluyoruz, genelde daha stabildir.
        print(f"Video Bağlantısı deneniyor: {VIDEO_URL}")
        self.cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)

        # Buffer boyutunu düşürerek gecikmeyi (latency) azaltmayı dene
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


        if not self.cap.isOpened():
            print("HATA: Video akışı açılamadı! URL veya ağ ayarlarını kontrol et.")
            return

        print("Video Akışı Başladı.")

        while self.calisiyor:
            ret, frame = self.cap.read()

            if ret:
                # --- A. KAYIT İŞLEMİ (İlk karede başlatılır) ---
                if not self.kayit_aktif:
                    self.kaydi_baslat(frame)

                # Diske yaz
                if self.out:
                    self.out.write(frame)

                # --- B. UI İÇİN DÖNÜŞTÜRME ---
                # OpenCV (BGR) -> Qt (RGB) dönüşümü
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w

                # QImage oluştur
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                # Sinyal ile UI'ya gönder (Ölçekleme UI tarafında yapılmalı)
                self.yeni_kare.emit(qt_image)
            else:
                # Veri gelmiyorsa işlemciyi yormamak için bekle
                print("Video verisi bekleniyor...")
                time.sleep(0.1)

        # Döngü biterse temizlik yap
        self.kapat()

    def kaydi_baslat(self, frame):
        """
        VideoWriter'ı ilk gelen karenin boyutuna göre başlatır.
        """
        height, width, layers = frame.shape
        # Codec: XVID (Daha evrenseldir) veya MP4V
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 20.0  # Tahmini FPS (Gelen yayına göre ayarlanmalı)

        self.out = cv2.VideoWriter(self.kayit_dosyasi, fourcc, fps, (width, height))
        self.kayit_aktif = True
        print(f"Video Kaydı Başladı: {self.kayit_dosyasi} | Çözünürlük: {width}x{height}")

    def kapat(self):
        print("Video Akışı Kapatılıyor...")
        self.calisiyor = False

        if self.cap:
            self.cap.release()

        if self.out:
            self.out.release()
            print("Kayıt dosyası kapatıldı ve kaydedildi.")

    def dur(self):
        """Dışarıdan çağrılan durdurma fonksiyonu"""
        self.calisiyor = False
        self.wait()