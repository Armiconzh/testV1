import subprocess
import time
import os

# Langkah 1: Menjalankan perintah turbostat
command = "sudo turbostat --enable all --interval 5 -out t1_log --quiet"
print("Menjalankan perintah turbostat...")
turbostat_process = subprocess.Popen(command, shell=True)

# Tunggu beberapa saat agar turbostat memulai
time.sleep(5)

# Langkah 2: Menjalankan code1.py
print("Menjalankan code1.py...")
code1_process = subprocess.Popen(["python3", "code1.py"])

# Langkah 3: Tunggu 6 detik sebelum menjalankan code2.py
time.sleep(6)

# Langkah 4: Menjalankan code2.py
print("Menjalankan code2.py...")
code2_process = subprocess.Popen(["python3", "code2.py"])

# Langkah 5: Menjalankan code3.py
print("Menjalankan code3.py...")
code3_process = subprocess.Popen(["python3", "code3.py"])

# Opsional: Tunggu proses selesai (jika diperlukan)
# code1_process.wait()
# code2_process.wait()
# code3_process.wait()

print("Pipeline selesai dijalankan.")
