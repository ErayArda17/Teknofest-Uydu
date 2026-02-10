import cv2
import subprocess
import sys


TARGET_IP = "192.168.1.124"
TARGET_PORT = 5600
CAMERA_INDEX = 0
FPS = 30
WIDTH = 640
HEIGHT = 480

def yayini_baslat():

    cap = cv2.VideoCapture(CAMERA_INDEX)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    if not cap.isOpened():
        print("HATA: Kamera açılamadı! Lütfen 'Sistem Ayarları > Gizlilik > Kamera' iznini kontrol edin.")
        return

    print(f"Kamera Başlatıldı: {WIDTH}x{HEIGHT} @ {FPS}fps")
    print(f"Yayın Hedefi: udp://{TARGET_IP}:{TARGET_PORT}")


    command = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',      # OpenCV'den gelen giriş formatı
        '-s', f"{WIDTH}x{HEIGHT}",
        '-r', str(FPS),
        '-i', '-',                # Stdin'den oku
        '-c:v', 'libx264',        # Yazılımsal encoder
        '-pix_fmt', 'yuv420p',    # <--- EKLENDİ: Çoğu oynatıcı için standart uyumluluk (4:4:4 yerine 4:2:0)
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-f', 'mpegts',           # UDP stream formatı
        f"udp://{TARGET_IP}:{TARGET_PORT}?pkt_size=1316"
    ]

    # 3. SUBPROCESS BAŞLAT (macOS UYUMLU)
    try:
        # Windows'a özgü olan 'creationflags' parametresi kaldırıldı.
        p = subprocess.Popen(command, stdin=subprocess.PIPE, shell=False)
    except FileNotFoundError:
        print("KRİTİK HATA: 'ffmpeg' komutu bulunamadı!")
        print("Çözüm: Terminali açıp 'brew install ffmpeg' komutunu çalıştırın.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Kameradan görüntü alınamıyor!")
                break

            # Frame'i byte'a çevirip ffmpeg'e gönder
            try:
                p.stdin.write(frame.tobytes())
            except BrokenPipeError:
                # FFmpeg beklenmedik şekilde kapanırsa
                print("Hata: FFmpeg bağlantısı koptu (Broken Pipe).")
                break
            except Exception as e:
                print(f"Yayın Hatası: {e}")
                break

    except KeyboardInterrupt:
        print("\nYayın kullanıcı tarafından durduruluyor...")
    finally:
        cap.release()
        if p.stdin:
            p.stdin.close()
        p.wait()
        print("Yayın sonlandırıldı.")

if __name__ == "__main__":
    yayini_baslat()