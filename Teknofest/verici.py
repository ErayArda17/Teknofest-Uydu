import cv2
import subprocess
import time

# --- AYARLAR ---
TARGET_IP = "192.168.1.124"  # Alıcının (Yer İstasyonunun) IP Adresi
TARGET_PORT = 5600  # Alıcının Dinlediği Port
CAMERA_INDEX = 0  # 0: Laptop Kamerası, 1: USB Kamera
FPS = 30
WIDTH = 640
HEIGHT = 480


def yayini_baslat():
    # 1. KAMERAYI AÇ
    cap = cv2.VideoCapture(CAMERA_INDEX)

    # Çözünürlüğü zorla (FFmpeg ayarlarıyla tutarlı olmalı)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    if not cap.isOpened():
        print("HATA: Kamera açılamadı!")
        return

    print(f"Kamera Başlatıldı: {WIDTH}x{HEIGHT} @ {FPS}fps")
    print(f"Yayın Hedefi: udp://{TARGET_IP}:{TARGET_PORT}")

    # 2. FFMPEG KOMUTUNU HAZIRLA
    # Bu komut ham görüntüyü alır, H.264'e çevirir ve MPEG-TS formatında UDP'den basar.
    # 'ultrafast' ve 'zerolatency' ayarları gecikmeyi minimuma indirir.
    command = [
        'ffmpeg',
        '-y',  # Varsa üzerine yaz
        '-f', 'rawvideo',  # Giriş formatı: Ham video
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',  # OpenCV renk formatı (BGR)
        '-s', f"{WIDTH}x{HEIGHT}",  # Çözünürlük
        '-r', str(FPS),  # Kare hızı
        '-i', '-',  # Giriş kaynağı: Pipe (Python'dan gelecek)
        '-c:v', 'libx264',  # Codec: H.264
        '-preset', 'ultrafast',  # En hızlı sıkıştırma (Gecikme için)
        '-tune', 'zerolatency',  # Canlı yayın optimizasyonu
        '-f', 'mpegts',  # Çıkış formatı: MPEG Transport Stream
        f"udp://{TARGET_IP}:{TARGET_PORT}?pkt_size=1316"  # Hedef
    ]

    # Subprocess'i başlat (Stdin üzerinden veri besleyeceğiz)
    try:
        # creationflags=subprocess.CREATE_NO_WINDOW -> Siyah CMD penceresi açılmasın diye (Windows)
        p = subprocess.Popen(command, stdin=subprocess.PIPE, shell=False)
    except FileNotFoundError:
        print("KRİTİK HATA: 'ffmpeg' bulunamadı! Lütfen FFmpeg yükle ve PATH'e ekle.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Kameradan görüntü alınamıyor!")
                break

            # 3. KAREYİ FFMPEG'E YAZ
            try:
                # Frame'i byte dizisine çevir ve ffmpeg'in stdin borusuna it
                p.stdin.write(frame.tobytes())
            except Exception as e:
                print(f"Yayın Hatası: {e}")
                break

    except KeyboardInterrupt:
        print("\nYayın durduruluyor...")
    finally:
        cap.release()
        p.stdin.close()
        p.wait()
        print("Kaynaklar serbest bırakıldı.")


if __name__ == "__main__":
    yayini_baslat()