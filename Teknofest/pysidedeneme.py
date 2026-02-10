import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QGridLayout,
                               QLabel, QVBoxLayout, QWidget, QFrame, QSizePolicy)
from PySide6.QtGui import QColor, QPalette, QPixmap, QImage
from PySide6.QtCore import Qt, Slot


from aras import Dinleyici
from alici import VideoAlici




class DurumKutusu(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setFixedSize(25, 25)
        self.renkayarla(color)

    def renkayarla(self, color):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)


class BaslikLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        self.setAlignment(Qt.AlignCenter)


class VeriLabel(QLabel):
    def __init__(self, text="0.00"):
        super().__init__(text)
        self.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold;
            color: #003366; 
            border: 1px solid #ccc; 
            background-color: #f0f0f0;
            border-radius: 4px;
            padding: 2px;
        """)
        self.setAlignment(Qt.AlignCenter)


# --- ANA PENCERE ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gazi Model Uydu - Yer İstasyonu v2.0")
        self.resize(1200, 700)  # Video için pencereyi biraz büyüttük

        # Ana Widget
        ana_widget = QWidget()
        ana_layout = QHBoxLayout()  # Sol: Video, Sağ: Veriler

        # ---------------------------------------------------------
        # 1. SOL PANEL: VİDEO EKRANI
        # ---------------------------------------------------------
        self.lbl_video = QLabel("Video Bağlantısı Bekleniyor...")
        self.lbl_video.setAlignment(Qt.AlignCenter)
        self.lbl_video.setStyleSheet("background-color: #000; color: #fff; font-size: 16px;")
        self.lbl_video.setMinimumSize(640, 480)  # Minimum video boyutu
        self.lbl_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Sol frame içine ekle
        sol_frame = QFrame()
        sol_frame.setFrameShape(QFrame.StyledPanel)
        sol_layout = QVBoxLayout()
        sol_layout.addWidget(self.lbl_video)
        sol_frame.setLayout(sol_layout)

        # ---------------------------------------------------------
        # 2. SAĞ PANEL: VERİLER VE DURUMLAR (DİKEY YAPI)
        # ---------------------------------------------------------
        sag_layout = QVBoxLayout()

        # --- A. Sayısal Veriler ---
        veri_group = QFrame()
        veri_group.setFrameShape(QFrame.Box)
        veri_grid = QGridLayout()

        # Etiketler
        self.lbl_paket_no = VeriLabel("0")
        self.lbl_yukseklik = VeriLabel("0.0 m")
        self.lbl_basinc = VeriLabel("0 hPa")
        self.lbl_hiz = VeriLabel("0 m/s")
        self.lbl_pil = VeriLabel("0.0 V")
        self.lbl_gps = VeriLabel("0.0, 0.0")

        veri_grid.addWidget(BaslikLabel("Paket No"), 0, 0)
        veri_grid.addWidget(self.lbl_paket_no, 1, 0)
        veri_grid.addWidget(BaslikLabel("Yükseklik"), 0, 1)
        veri_grid.addWidget(self.lbl_yukseklik, 1, 1)
        veri_grid.addWidget(BaslikLabel("Basınç"), 2, 0)
        veri_grid.addWidget(self.lbl_basinc, 3, 0)
        veri_grid.addWidget(BaslikLabel("İniş Hızı"), 2, 1)
        veri_grid.addWidget(self.lbl_hiz, 3, 1)
        veri_grid.addWidget(BaslikLabel("Pil Voltajı"), 4, 0)
        veri_grid.addWidget(self.lbl_pil, 5, 0)
        veri_grid.addWidget(BaslikLabel("GPS Konum"), 4, 1)
        veri_grid.addWidget(self.lbl_gps, 5, 1)

        veri_group.setLayout(veri_grid)

        # --- B. Durum Kutuları ---
        durum_group = QFrame()
        durum_group.setFrameShape(QFrame.Box)
        durum_grid = QGridLayout()

        self.inisrenk = DurumKutusu('green')
        self.yukrenk = DurumKutusu('green')
        self.basincrenk = DurumKutusu('green')
        self.konumrenk = DurumKutusu('green')
        self.ayrilmarenk = DurumKutusu('green')
        self.filtrerenk = DurumKutusu('green')

        durum_grid.addWidget(BaslikLabel("İniş Hızı"), 0, 0)
        durum_grid.addWidget(self.inisrenk, 1, 0)
        durum_grid.addWidget(BaslikLabel("Basınç"), 0, 1)
        durum_grid.addWidget(self.basincrenk, 1, 1)
        durum_grid.addWidget(BaslikLabel("Yükseklik"), 0, 2)
        durum_grid.addWidget(self.yukrenk, 1, 2)
        durum_grid.addWidget(BaslikLabel("Filtre"), 2, 0)
        durum_grid.addWidget(self.filtrerenk, 3, 0)
        durum_grid.addWidget(BaslikLabel("Ayrılma"), 2, 1)
        durum_grid.addWidget(self.ayrilmarenk, 3, 1)
        durum_grid.addWidget(BaslikLabel("Konum"), 2, 2)
        durum_grid.addWidget(self.konumrenk, 3, 2)

        durum_group.setLayout(durum_grid)

        # Sağ panele ekle
        sag_layout.addWidget(QLabel("TELEMETRİ VERİLERİ"))
        sag_layout.addWidget(veri_group)
        sag_layout.addSpacing(20)
        sag_layout.addWidget(QLabel("SİSTEM DURUMU"))
        sag_layout.addWidget(durum_group)
        sag_layout.addStretch()  # Altta boşluk bırak

        sag_frame = QFrame()
        sag_frame.setLayout(sag_layout)

        # ---------------------------------------------------------
        # 3. ANA LAYOUT BİRLEŞTİRME
        # ---------------------------------------------------------
        ana_layout.addWidget(sol_frame, 65)  # Ekranın %65'i video
        ana_layout.addWidget(sag_frame, 35)  # Ekranın %35'i veri

        ana_widget.setLayout(ana_layout)
        self.setCentralWidget(ana_widget)

        # ---------------------------------------------------------
        # 4. THREAD BAŞLATMA (VERİ + VİDEO)
        # ---------------------------------------------------------

        # A) Sensör Verisi Dinleyici
        self.dinleyen = Dinleyici()
        self.dinleyen.veri.connect(self.veriisleme)
        self.dinleyen.start()

        # B) Video Alıcı
        self.video_thread = VideoAlici()
        self.video_thread.yeni_kare.connect(self.videoguncelle)
        self.video_thread.start()

    # --- SLOT FONKSİYONLARI ---

    @Slot(QImage)
    def videoguncelle(self, image):
        """Video thread'inden gelen kareyi ekrana basar"""
        # QImage -> QPixmap dönüşümü
        pixmap = QPixmap.fromImage(image)

        # Görüntüyü label boyutuna oranlı sığdır (KeepAspectRatio)
        w = self.lbl_video.width()
        h = self.lbl_video.height()

        self.lbl_video.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))

    def veriisleme(self, paketler):
        """Telemetri verisini işler ve Hataları Gösterir"""

        # DEBUG: Verinin gelip gelmediğini konsolda görmek için bu satırı açabilirsin
        # print(f"Gelen Paket: {paketler}")

        try:
            # GÜVENLİ DÖNÜŞÜM: Gelen veri string bile olsa float'a çevirip öyle yazdırıyoruz.
            # Paket indeksleri: 0:No, 1:Durum, 2:Basınç1, 3:Basınç2, 4:Yükseklik...

            # 1. Paket Numarası (Integer)
            self.lbl_paket_no.setText(str(int(paketler[0])))

            # 2. Yükseklik (Float - Virgülden sonra 2 basamak)
            # Not: float() kullanımı, veri string gelse bile ("500.00") onu sayıya çevirir hatayı önler.
            self.lbl_yukseklik.setText(f"{float(paketler[4]):.2f} m")

            # 3. Basınç
            self.lbl_basinc.setText(f"{float(paketler[2]):.2f} hPa")

            # 4. İniş Hızı (İndeks 7 varsayıldı)
            self.lbl_hiz.setText(f"{float(paketler[7]):.2f} m/s")

            # 5. Pil Voltajı (İndeks 9 varsayıldı)
            self.lbl_pil.setText(f"{float(paketler[9]):.2f} V")

            lat = float(paketler[10])
            lon = float(paketler[11])
            self.lbl_gps.setText(f"{lat:.4f}\n{lon:.4f}")


            statü = int(paketler[1])


            def renk_sec(durum):
                return "red" if durum else "green"


            self.inisrenk.renkayarla(renk_sec((statü >> 0) & 1))  # 0. Bit
            self.basincrenk.renkayarla(renk_sec((statü >> 1) & 1))  # 1. Bit
            self.yukrenk.renkayarla(renk_sec((statü >> 2) & 1))  # 2. Bit
            self.filtrerenk.renkayarla(renk_sec((statü >> 3) & 1))  # 3. Bit
            self.ayrilmarenk.renkayarla(renk_sec((statü >> 4) & 1))  # 4. Bit
            self.konumrenk.renkayarla(renk_sec((statü >> 5) & 1))  # 5. Bit

        except IndexError:
            print("HATA: Gelen paket eksik veya indeksler yanlış!")
        except ValueError as e:
            print(f"HATA: Veri tipi dönüştürülemedi! Gelen veri sayı değil mi? Detay: {e}")
        except Exception as e:
            # Burası hatayı gizlemek yerine konsola basacak
            print(f"Arayüz Güncelleme Hatası: {e}")
    def closeEvent(self, event):
        """Pencere kapanırken threadleri güvenli durdur"""
        print("Sistem Kapatılıyor...")
        self.dinleyen.dur()
        self.video_thread.dur()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())