import random
import socket
import struct
import time

telsiz = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

Format = "<I B 17f B"
paketno = 1

print("Özel Protokol Simülasyonu Başladı...")

while True:
    time.sleep(1)

    # --- Sensör Verileri ---
    basinc_1 = 1013.25 + random.uniform(-2, 2)
    basinc_2 = 1012.80 + random.uniform(-2, 2)
    yukseklik_1 = 1250.0 - random.uniform(0, 50)
    yukseklik_2 = 1250.0 - random.uniform(0, 50)
    irtifa_farki = abs(yukseklik_1 - yukseklik_2)
    inis_hizi = 12.5 + random.uniform(-1.5, 1.5)
    sicaklik = 24.5 + random.uniform(-0.5, 0.5)
    pil_gerilimi = 7.6 - random.uniform(0, 0.2)
    gps_lat = 39.7804 + random.uniform(-0.0001, 0.0001)
    gps_long = 32.8048 + random.uniform(-0.0001, 0.0001)
    gps_alt = yukseklik_1 + 15.0
    pitch = random.uniform(-10, 10)
    roll = random.uniform(-10, 10)
    yaw = random.uniform(0, 360)
    rhrh = 45.0 + random.uniform(-5, 5)
    iot_data_1 = 22.4
    iot_data_2 = 1011.2

    # --- Bitwise İşlemler ---
    durumlar = [0, 1, 0, 1, 1, 1]
    paket_durum = 0
    sayi = 0
    for i in durumlar:
        if i == 1:
            paket_durum += (2 ** sayi)
        sayi += 1

    # --- ADIM 1: Veriyi Checksum OLMADAN geçici paketle ---
    # Checksum'ı hesaplamak için önce verinin ham haline ihtiyacımız var
    temp_format = "<I B 17f"
    raw_data = struct.pack(temp_format, paketno, paket_durum, basinc_1, basinc_2, yukseklik_1, yukseklik_2,
                           irtifa_farki, inis_hizi, sicaklik, pil_gerilimi, gps_lat, gps_long,
                           gps_alt, pitch, roll, yaw, rhrh, iot_data_1, iot_data_2)

    # --- ADIM 2: Checksum Hesapla (Basit Toplama Yöntemi) ---
    # Paketteki tüm byte'ları topla ve 256'ya bölümünden kalanı al (0-255 arası sayı çıkar)
    checksum = sum(raw_data) % 256

    # --- ADIM 3: Checksum'ı sona ekle ve asıl paketi oluştur ---
    # raw_data'nın ucuna checksum byte'ını ekliyoruz
    final_packet = raw_data + struct.pack("B", checksum)

    # Gönder
    telsiz.sendto(final_packet, ("127.0.0.1", 5005))

    print(f"Paket: {paketno} | Durum: {paket_durum} | Checksum: {checksum}")
    paketno += 1