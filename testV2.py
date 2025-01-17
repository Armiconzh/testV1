import pandas as pd
import time
import os

# Definisikan jalur file
file_path = 'TURBOSTAT_log.csv'
output_path = 'filtered_turbolog.csv'

# Fungsi untuk membaca dan memfilter data
def filter_data():
    # Membaca file CSV
    df = pd.read_csv(file_path)

    # Hapus baris pertama jika mengandung header duplikat
    df = df[df["Core"] != "Core"]

    # Filter data untuk Core 0-5
    df_filtered = df[(df['Core'] == '-') | (df['CPU'] == '-')]

    # Simpan ke file baru
    df_filtered.to_csv(output_path, index=False, sep='\t')

# Fungsi untuk memeriksa apakah file telah berubah
def file_has_changed(last_modified_time):
    return os.path.getmtime(file_path) > last_modified_time

# Perulangan untuk memantau perubahan file
def start_monitoring():
    last_modified_time = os.path.getmtime(file_path)  # Mendapatkan waktu terakhir file dimodifikasi

    while True:
        time.sleep(1)  # Tunggu 1 detik sebelum memeriksa lagi

        if file_has_changed(last_modified_time):  # Cek jika file sudah berubah
            print(f"{file_path} telah diperbarui. Memperbarui {output_path}...")
            filter_data()  # Update file output dengan data yang sudah difilter
            last_modified_time = os.path.getmtime(file_path)  # Update waktu terakhir file dimodifikasi

if __name__ == "__main__":
    print("Memulai pemantauan perubahan file...")
    start_monitoring()
