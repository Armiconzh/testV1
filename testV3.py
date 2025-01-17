import time
import csv

# Fungsi untuk membaca data dari file TURBOSTAT_log
def read_turbostat_log(file_path):
    try:
        with open(file_path, 'r') as f:
            # Membaca seluruh data dari file
            data = f.readlines()
        return data
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan.")
        return []

# Fungsi untuk menulis data ke file CSV
def write_to_csv(csv_path, data):
    try:
        with open(csv_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Menulis data ke CSV file
            writer.writerow(data)
    except Exception as e:
        print(f"Terjadi kesalahan saat menulis ke CSV: {e}")

# Fungsi untuk memproses data dan memperbarui CSV
def process_and_update_data():
    log_file = './TURBOSTAT_log'
    csv_file = 'TURBOSTAT_log.csv'
    previous_data = []

    while True:
        # Membaca data terbaru dari file TURBOSTAT_log
        current_data = read_turbostat_log(log_file)

        if current_data != previous_data:
            # Jika data berubah, update file CSV
            for line in current_data:
                # Proses data per baris jika perlu (misalnya, memecah berdasarkan delimiter)
                row = line.strip().split()  # Sesuaikan split dengan format data Anda

                # Menulis data ke file CSV
                write_to_csv(csv_file, row)

            # Simpan data terakhir yang sudah diproses
            previous_data = current_data

        # Tunggu 1 detik sebelum memeriksa lagi
        time.sleep(1)

if __name__ == "__main__":
    process_and_update_data()
