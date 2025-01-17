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

# Fungsi untuk menulis data ke file CSV dengan tab sebagai delimiter
def write_to_csv(csv_path, data):
    try:
        with open(csv_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')  # Gunakan tab sebagai delimiter
            # Menulis data ke CSV file
            writer.writerow(data)
    except Exception as e:
        print(f"Terjadi kesalahan saat menulis ke CSV: {e}")

# Fungsi untuk membaca data yang sudah ada di CSV (untuk mencegah duplikasi)
def read_existing_csv(csv_path):
    existing_data = set()
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')  # Gunakan tab sebagai delimiter
            for row in reader:
                existing_data.add(tuple(row))  # Menggunakan tuple untuk perbandingan
    except FileNotFoundError:
        pass  # Jika file CSV belum ada, kita anggap data masih kosong
    return existing_data

# Fungsi untuk memproses data dan memperbarui CSV tanpa duplikasi
def process_and_update_data():
    log_file = './TURBOSTAT_log'
    csv_file = 'TURBOSTAT_log.csv'
    
    # Membaca data yang sudah ada di CSV untuk mencegah duplikasi
    existing_data = read_existing_csv(csv_file)

    while True:
        # Membaca data terbaru dari file TURBOSTAT_log
        current_data = read_turbostat_log(log_file)

        for line in current_data:
            # Proses data per baris jika perlu (misalnya, memecah berdasarkan delimiter)
            row = tuple(line.strip().split())  # Mengubah baris menjadi tuple untuk perbandingan

            # Jika baris ini belum ada di CSV, maka tambahkan
            if row not in existing_data:
                write_to_csv(csv_file, row)
                existing_data.add(row)  # Menambahkan data baru ke set

        # Tunggu 1 detik sebelum memeriksa lagi
        time.sleep(1)

if __name__ == "__main__":
    process_and_update_data()