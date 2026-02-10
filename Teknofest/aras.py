import socket
import struct
import csv
import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal

# --- AYARLAR ---
UDP_IP = "192.168.1.124"
UDP_PORT = 5005


class Dinleyici(QThread):
    # Sinyal tüm paketi (liste olarak) arayüze taşıyacak
    veri = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calisiyor = True
        self.socket = None

        # Log Dosyası Oluşturma
        zaman = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.dosya_adi = f"UcusLog_{zaman}.csv"

        # CSV Başlıkları
        with open(self.dosya_adi, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "PaketNo", "Durum", "Basinc1", "Basinc2", "Yuk1", "Yuk2",
                "Fark", "InisHizi", "Sicaklik", "Pil", "Lat", "Long", "Alt",
                "Pitch", "Roll", "Yaw", "Nem", "GorevHiz", "IoT2", "Zaman"
            ])

    def run(self):
        # 1. UDP SOCKET'İ AÇ
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((UDP_IP, UDP_PORT))
            self.socket.settimeout(1.0)  # Timeout ekle ki dur() fonksiyonu çalışabilsin
            print(f"UDP Bağlantısı Başarılı: {UDP_IP}:{UDP_PORT}")
        except Exception as e:
            print(f"HATA: UDP Socket Açılamadı! ({e})")
            return

        print("UDP veri bekleniyor (74 Byte)...")

        while self.calisiyor:
            try:
                # 2. UDP VERİSİNİ OKUMA
                data, addr = self.socket.recvfrom(1024)  # Maksimum 1024 byte oku

                # Gelen veri tam 74 byte mi kontrol et
                if len(data) == 74:
                    self.paketi_isle(data)
                    print(f"Veri geldi: {addr} -> {len(data)} byte")
                else:
                    print(f"Yanlış paket boyutu: {len(data)} byte (74 bekleniyordu)")

            except socket.timeout:
                # Timeout oldu, döngüyü devam ettir (dur() için)
                continue
            except Exception as e:
                if self.calisiyor:  # Sadece hala çalışıyorsa hata yazdır
                    print(f"UDP Veri Okuma Hatası: {e}")
                time.sleep(0.1)

    def paketi_isle(self, data):
        """
        Ham binary veriyi (74 byte) çözer, doğrular ve arayüze yollar.
        """
        try:
            # --- A. CHECKSUM KONTROLÜ ---
            payload = data[:-1]  # İlk 73 Byte
            gelen_checksum = data[-1]  # Son Byte (74.)

            hesaplanan = sum(payload) % 256

            if gelen_checksum != hesaplanan:
                print(f"Checksum Hatası! (Gelen: {gelen_checksum}, Hesaplanan: {hesaplanan})")
                return  # Hatalı paketi atla

            # --- B. VERİYİ ÇÖZ (UNPACK) ---
            # Format: < (Little Endian), I (4), B (1), 17f (68) = 73 Byte
            values = struct.unpack("<I B 17f", payload)

            # --- C. LİSTEYİ HAZIRLA ---
            gonderilecek_paket = []

            # 1. Paket No ve Durum
            gonderilecek_paket.append(str(values[0]))  # Paket No
            gonderilecek_paket.append(str(values[1]))  # Durum Kodu

            # 2. Float Değerler (Virgülden sonra 2 basamak)
            for val in values[2:]:
                gonderilecek_paket.append(f"{val:.2f}")

            # --- D. LOGLAMA ---
            with open(self.dosya_adi, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Listeye zaman damgası ekleyip yaz
                log_row = list(values)
                log_row.append(datetime.now().strftime("%H:%M:%S.%f"))
                writer.writerow(log_row)

            # --- E. ARAYÜZE GÖNDER ---
            self.veri.emit(gonderilecek_paket)

            # Terminale de yaz (Canlı izlemek için)
            if len(values) > 4:  # Yükseklik var mı kontrol et
                print(f"Paket #{values[0]} OK | Yükseklik: {values[4]:.2f}m | Hız: {values[7]:.2f}m/s")
            else:
                print(f"Paket #{values[0]} OK")

        except struct.error as e:
            print(f"Struct Unpack Hatası: {e}")
        except Exception as e:
            print(f"Paket Çözme Hatası: {e}")

    def dur(self):
        self.calisiyor = False
        if self.socket:
            self.socket.close()
        self.wait()  # Thread'in tamamen durmasını bekle
