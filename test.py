import sqlite3

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

# user tablosundaki tüm kayıtları al
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Sütun adlarını al
column_names = [description[0] for description in cursor.description]

# Tablo başlığı
print("-" * 80)
print(" | ".join(column_names))
print("-" * 80)

# Satırları yazdır
for row in rows:
    print(" | ".join(str(value) for value in row))

print("-" * 80)

conn.close()