import pandas as pd
import os

# Excel fayl manzili
file_path = "SOATO.xlsx"

# Excel faylini yuklash (faqat A va B ustunlari kerak)
df = pd.read_excel(file_path, sheet_name="uz", usecols=[0, 1], names=["code", "name"])
df["code"] = df["code"].astype(str)  # Kodlarni stringga aylantiramiz

# Foydalanuvchilar uchun alohida papka yaratamiz
output_folder = "address_data"
os.makedirs(output_folder, exist_ok=True)

# Viloyatlar (4 xonali kodlar)
regions = df[df["code"].str.match(r"^\d{4}$")].copy()

# Tumanlar (7 xonali kodlar)
districts = df[df["code"].str.match(r"^\d{7}$")].copy()

# Ko‘chalar (10 xonali kodlar)
streets = df[df["code"].str.match(r"^\d{10}$")].copy()

# Har bir viloyat uchun alohida CSV yaratish
for _, region in regions.iterrows():
    region_code = region["code"]
    region_name = region["name"]

    # Viloyat papkasini yaratish
    region_folder = os.path.join(output_folder, region_name)
    os.makedirs(region_folder, exist_ok=True)

    # Shu viloyatga tegishli tumanlar
    region_districts = districts[districts["code"].str.startswith(region_code)]
    region_districts.to_csv(f"{region_folder}/districts.csv", index=False, encoding="utf-8")

    # Har bir tuman uchun ko‘cha ro‘yxatini yaratish
    for _, district in region_districts.iterrows():
        district_code = district["code"]
        district_name = district["name"]

        # Shu tumanga tegishli ko‘chalar
        district_streets = streets[streets["code"].str.startswith(district_code)]
        district_streets.to_csv(f"{region_folder}/{district_name}.csv", index=False, encoding="utf-8")

print("Barcha viloyatlar, tumanlar va ko‘chalar uchun CSV fayllar yaratildi!")
