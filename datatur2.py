import pandas as pd
import numpy as np

# --- 1. Pembersihan Data ---

# Baca file CSV dengan baris pertama sebagai header
df = pd.read_csv('./test1mico.csv')

# Simpan nama kolom (header) dalam list
header = df.columns.tolist()

# Hapus baris yang merupakan header berulang (baris yang seluruh nilainya sama dengan header)
mask_header = (df.astype(str) == pd.Series(header, index=df.columns)).all(axis=1)
df_clean = df[~mask_header]

# Hapus baris yang pada kolom "Core" berisi "-"
df_clean = df_clean[df_clean['Core'] != '-']

# Reset index agar rapi
df_clean.reset_index(drop=True, inplace=True)

# --- 5. Simpan dan Tampilkan Hasil Akhir ---
df_clean.to_csv('./data_final1clean.csv', index=False)
print(df_clean)
