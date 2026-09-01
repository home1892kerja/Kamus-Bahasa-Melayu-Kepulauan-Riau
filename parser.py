import pandas as pd
import uuid
import re
import os

def parse_lexicon(file_path):
    # Membaca file TXT
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    rows = []
    
    # Kamus Pemetaan Wilayah & Register
    region_map = {
        'Nat': 'Natuna', 'Lin': 'Lingga', 'Bin': 'Bintan',
        'Kar': 'Karimun', 'Tam': 'Tambelan', 'PuT': 'Pulau Tujuh', 'Sek': 'Sekat/Singkep'
    }
    usage_map = {'ki': 'kiasan', 'kas': 'kasar'}

    # State Trackers
    state = {'lemma': '', 'homonym_id': '', 'subentry': '', 'sense_id': '', 'pos': '', 'region': '', 'usage_label': ''}
    current_record = {'definition': '', 'example_source': '', 'example_translation': '', 'semantic_note': '', 'cross_reference': ''}

    def push_record():
        if state['lemma'] and (current_record['definition'] or state['pos'] or state['subentry']):
            rows.append({
                'entry_id': str(uuid.uuid4()),
                'lemma': state['lemma'],
                'subentry': state['subentry'],
                'homonym_id': state['homonym_id'],
                'sense_id': state['sense_id'],
                'pos': state['pos'],
                'region': state['region'],
                'usage_label': state['usage_label'],
                'definition': current_record['definition'],
                'example_source': current_record['example_source'],
                'example_translation': current_record['example_translation'],
                'semantic_note': current_record['semantic_note'],
                'cross_reference': current_record['cross_reference']
            })
        # Reset current record
        for key in current_record:
            current_record[key] = ''

    # Looping baris demi baris menggunakan RegEx
    for line in lines:
        line = line.strip()
        if not line: continue

        match = re.match(r'^\\([a-z]+)\s*(.*)', line)
        if not match: continue

        marker, value = match.groups()
        value = value.strip()

        if marker == 'lx':
            push_record()
            state = {k: '' for k in state} # Reset total
            state['lemma'] = value if value else None
        elif marker == 'hm':
            state['homonym_id'] = value
        elif marker == 'se':
            push_record()
            state['subentry'] = value
            state['sense_id'] = ''
            state['pos'] = ''
            state['region'] = ''
            state['usage_label'] = ''
        elif marker == 'sn':
            push_record()
            state['sense_id'] = value
        elif marker == 'ps':
            parts = value.split(' ')
            state['pos'] = parts[0] if parts else ''
            if len(parts) > 1:
                for part in parts[1:]:
                    if part in region_map: state['region'] = region_map[part]
                    elif part in usage_map: state['usage_label'] = usage_map[part]
        elif marker == 'dn': current_record['definition'] = value
        elif marker == 'xv': current_record['example_source'] = value
        elif marker == 'xn': current_record['example_translation'] = value
        elif marker == 'gn': current_record['semantic_note'] = value
        elif marker == 'sy': current_record['cross_reference'] = value

    push_record() # Amankan baris terakhir
    
    return pd.DataFrame(rows)

# ==========================================
# EKSEKUSI UTAMA
# ==========================================
input_filename = 'DATA KAMUS 2026.txt'
output_filename = 'Database_Kamus_Kepri.xlsx'

print("Memulai ekstraksi data...")

if os.path.exists(input_filename):
    df = parse_lexicon(input_filename)
    df.to_excel(output_filename, index=False)
    print(f"✅ Selesai! {len(df)} baris data berhasil diekstrak dan disimpan ke '{output_filename}'.")
else:
    print(f"❌ Error: File '{input_filename}' tidak ditemukan. Pastikan nama file dan foldernya benar.")