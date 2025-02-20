import pandas as pd
import numpy as np

# --- 1. Pembersihan Data ---

# Baca file CSV dengan baris pertama sebagai header
df = pd.read_csv('./TURBOSTAT_log.csv')

# Simpan nama kolom (header) dalam list
header = df.columns.tolist()

# Hapus baris yang merupakan header berulang (baris yang seluruh nilainya sama dengan header)
mask_header = (df.astype(str) == pd.Series(header, index=df.columns)).all(axis=1)
df_clean = df[~mask_header]

# Hapus baris yang pada kolom "Core" berisi "-"
df_clean = df_clean[df_clean['Core'] != '-']

# Reset index agar rapi
df_clean.reset_index(drop=True, inplace=True)

# Jika nilai pada kolom Core berupa angka (0 sampai 71) dan saat ini masih string, konversikan ke integer
df_clean['Core'] = df_clean['Core'].astype(int)

# --- 2. Menentukan Blok Kontigu Berdasarkan Perubahan Nilai Core ---
# Setiap kali nilai di kolom Core berubah, kita anggap mulai blok baru.
df_clean['block_id'] = (df_clean['Core'] != df_clean['Core'].shift()).cumsum()

# --- 3. Agregasi Setiap 4 Baris Kontigu Sesuai Urutan Asli ---
aggregated_rows = []

# Iterasi per blok (sesuai urutan asli data, tanpa mengurutkan ulang)
for block_id, block in df_clean.groupby('block_id', sort=False):
    block = block.reset_index(drop=True)
    # Bagi blok menjadi chunk berukuran 4 baris
    for i in range(0, len(block), 4):
        chunk = block.iloc[i:i+4]
        agg_row = {}
        # Proses tiap kolom (kecuali kolom pembantu block_id)
        for col in block.columns:
            if col == 'block_id':
                continue
            if col == 'Core':
                # Untuk kolom Core, karena seluruh baris pada chunk memiliki nilai yang sama, ambil nilai pertama
                agg_row[col] = chunk[col].iloc[0]
            else:
                # Jika kolom bersifat numerik, hitung rata-rata; jika non-numerik, ambil nilai baris pertama
                if pd.api.types.is_numeric_dtype(chunk[col]):
                    agg_row[col] = chunk[col].mean()
                else:
                    agg_row[col] = chunk[col].iloc[0]
        aggregated_rows.append(agg_row)

# Buat DataFrame dari hasil agregasi
df_aggregated = pd.DataFrame(aggregated_rows)

# --- 4. Tambahkan Kolom Time_Of_Day_Seconds ---
# Mekanisme:
#   - Diasumsikan bahwa urutan data adalah complete cycle: setiap 72 baris mewakili Core 0 sampai 71.
#   - Baris 0-71 akan diberi waktu 1737210251, baris 72-143 diberi waktu 1737210252, dan seterusnya.
base_time = 1737210251
# Perhitungan: bagi index baris dengan 72 (integer division) dan tambahkan ke base_time.
df_aggregated['Time_Of_Day_Seconds'] = (df_aggregated.index // 64) + base_time

# --- 5. Simpan dan Tampilkan Hasil Akhir ---
df_aggregated.to_csv('./data_final4.csv', index=False)
print(df_aggregated)
