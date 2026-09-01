import pandas as pd
import json

# 1. Baca fail Excel
df = pd.read_excel('Database_Kamus_Kepri.xlsx')
df = df.fillna('')

kamus_dict = {}

for index, row in df.iterrows():
    lema = str(row['lemma']).strip()
    subentry = str(row['subentry']).strip()
    homonym = int(row['homonym_id']) if row['homonym_id'] != '' else 0
    rujukan = str(row['cross_reference']).strip()
    
    kunci_lema = f"{lema}_{homonym}"
    
    if kunci_lema not in kamus_dict:
        kamus_dict[kunci_lema] = {
            "lema": lema,
            "homonim": homonym if homonym > 0 else None,
            "kelas_kata": row['pos'] if row['pos'] != '' else None,
            "pelafalan": lema, # Sesuaikan jika ada kolom pelafalan khusus
            "rujukan": rujukan,
            "definisi": [],
            "contoh_kalimat": [],
            "turunan": []
        }
    
    # Jika baris adalah lema utama
    if not subentry:
        if row['definition'] != '':
            kamus_dict[kunci_lema]['definisi'].append(row['definition'])
        if row['example_source'] != '':
            kamus_dict[kunci_lema]['contoh_kalimat'].append({
                "contoh": row['example_source'],
                "terjemahan": row['example_translation']
            })
    # Jika baris adalah sublema / turunan
    else:
        # Cek apakah sublema ini sudah ada di list turunan
        turunan_ada = next((t for t in kamus_dict[kunci_lema]['turunan'] if t['lema_turunan'] == subentry), None)
        if not turunan_ada:
            turunan_ada = {
                "lema_turunan": subentry,
                "kelas_kata": row['pos'] if row['pos'] != '' else None,
                "definisi": [],
                "contoh_kalimat": []
            }
            kamus_dict[kunci_lema]['turunan'].append(turunan_ada)
        
        if row['definition'] != '':
            turunan_ada['definisi'].append(row['definition'])
        if row['example_source'] != '':
            turunan_ada['contoh_kalimat'].append({
                "contoh": row['example_source'],
                "terjemahan": row['example_translation']
            })

hasil_json = list(kamus_dict.values())

with open('kamus_kepri_2026.json', 'w', encoding='utf-8') as f:
    json.dump(hasil_json, f, ensure_ascii=False, indent=4)

print(f"Berhasil merapikan {len(hasil_json)} entri leksikon!")