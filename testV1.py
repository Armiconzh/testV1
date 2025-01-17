import pandas as pd
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
    df_filtered.to_csv(output_path, index=False)

# Event handler untuk file yang berubah
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Memastikan hanya file yang dimaksud yang diubah
        if event.src_path == file_path:
            print(f"{file_path} telah diperbarui. Memperbarui {output_path}...")
            filter_data()

# Memulai pengamat untuk memantau perubahan file
def start_watching():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)  # Memantau perubahan di direktori saat ini
    observer.start()

    try:
        while True:
            time.sleep(1)  # Memeriksa setiap detik
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Memulai pemantauan
if __name__ == "__main__":
    print("Memulai pemantauan perubahan file...")
    start_watching()