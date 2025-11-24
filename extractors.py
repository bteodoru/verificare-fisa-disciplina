"""
Modul pentru extragerea datelor din fișa disciplinei în format DOCX.
Folosește indexare directă pentru acces rapid la celule.
"""
import re
from docx import Document
from typing import Dict, Optional


def clean_text(text: str) -> str:
    """Curăță textul de spații multiple și caractere speciale."""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_fisa_disciplina(file_path: str) -> Dict[str, any]:
    """
    Extrage datele din fișa disciplinei folosind indexare directă.
    
    Structura fișei (indexare 0-based):
    - Tabel 1 (index 1): Date despre disciplină
      - Rând 0, Celula 4: Denumiri (română / engleză)
      - Rând 1, Celula 4: Cod disciplină
      - Rând 1, Celula 8: Categoria (DA/DOP/DOB/DFA)
      - Rând 4, Celula 6: Evaluare (E/V/C)
    
    - Tabel 2 (index 2): Ore pe săptămână
      - Rând 0, Celula 4: Ore curs
      - Rând 0, Celula 8: Ore laborator
    
    Args:
        file_path: Calea către fișierul DOCX
        
    Returns:
        Dicționar cu datele extrase
    """
    doc = Document(file_path)
    
    result = {
        'cod': None,
        'denumire_ro': None,
        'denumire_en': None,
        'categoria': None,
        'nr_ore_saptamana': {
            'curs': 0,
            'seminar': 0,
            'proiect': 0,
            'lucrari': 0
        },
        'evaluare': None
    }
    
    try:
        # Tabelul 2 (index 1) - Date despre disciplină
        table_disciplina = doc.tables[1]
        
        # Denumiri - Rând 0, Celula 4
        denumiri_text = clean_text(table_disciplina.rows[0].cells[4].text)
        if '/' in denumiri_text:
            parts = denumiri_text.split('/')
            result['denumire_ro'] = clean_text(parts[0])
            result['denumire_en'] = clean_text(parts[1]) if len(parts) > 1 else None
        
        # Cod - Rând 1, Celula 4
        cod_text = clean_text(table_disciplina.rows[1].cells[4].text)
        match = re.search(r'([A-Z]{2}\.[A-Z]{2}\.\d{3})', cod_text)
        if match:
            result['cod'] = match.group(1)
        
        # Categoria - Rând 1, Celula 8
        categoria_text = clean_text(table_disciplina.rows[1].cells[8].text)
        match = re.search(r'\b(DA|DOP|DOB|DFA)\b', categoria_text)
        if match:
            result['categoria'] = match.group(1)
        
        # Evaluare - Rând 4, Celula 6
        evaluare_text = clean_text(table_disciplina.rows[4].cells[6].text)
        match = re.search(r'\b([EVC])\b', evaluare_text)
        if match:
            result['evaluare'] = match.group(1)
        
        # Tabelul 3 (index 2) - Ore pe săptămână
        table_ore = doc.tables[2]
        
        # Ore curs - Rând 0, Celula 4
        ore_curs_text = clean_text(table_ore.rows[0].cells[4].text)
        match = re.search(r'\b(\d+)\b', ore_curs_text)
        if match:
            result['nr_ore_saptamana']['curs'] = int(match.group(1))
        
        # Ore laborator - Rând 0, Celula 8
        ore_lab_text = clean_text(table_ore.rows[0].cells[8].text)
        match = re.search(r'\b(\d+)\b', ore_lab_text)
        if match:
            result['nr_ore_saptamana']['lucrari'] = int(match.group(1))
        
        # Seminar și proiect rămân 0 (nu sunt în structura actuală)
        
    except IndexError as e:
        print(f"Eroare la accesarea structurii: {e}")
    
    return result

if __name__ == '__main__':
    # Test pe fișa încărcată
    import json
    
    fisa_path = '/mnt/user-data/uploads/IGIA202_Modelare_in__ingineria_geotehnica_Teodoru_2.docx'
    
    print("Extrag datele din fișa disciplinei...")
    date = extract_fisa_disciplina(fisa_path)
    
    print("\n=== DATE EXTRASE ===")
    print(json.dumps(date, indent=2, ensure_ascii=False))

