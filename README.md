# Verificare Fișe Disciplină

Sistem automatizat pentru verificarea conformității fișelor de disciplină cu planul de învățământ.

## Descriere

Acest proiect extrage automat datele din fișele de disciplină (format DOCX) și le compară cu planul de învățământ pentru a identifica inconsistențe.

## Funcționalități

- ✅ Extragere automată din fișe DOCX
- ✅ Comparație cu planul de învățământ
- ✅ Detectare diferențe (exact match + fuzzy matching)
- ✅ Raportare în format JSON

## Structura Proiectului

```
verificare-fisa/
├── extractors.py           # Extracție date din DOCX
├── validators.py           # Validare față de plan (în dezvoltare)
├── plan_invatamant.json    # Plan de învățământ (exemplu)
├── requirements.txt        # Dependințe Python
├── README.md              # Documentație
└── .gitignore             # Fișiere ignorate de git
```

## Instalare

### 1. Clonează repository-ul

```bash
git clone https://github.com/USERNAME/verificare-fisa.git
cd verificare-fisa
```

### 2. Creează virtual environment

```bash
python -m venv venv
```

### 3. Activează virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalează dependințele

```bash
pip install -r requirements.txt
```

## Utilizare

### Extragere date din fișă

```python
from extractors import extract_fisa_disciplina

# Extrage datele din fișa DOCX
date = extract_fisa_disciplina('cale/catre/fisa.docx')

print(date)
# Output:
# {
#   'cod': 'IG.IA.202',
#   'denumire_ro': 'Modelare în ingineria geotenică',
#   'denumire_en': 'Modelling in Geotechnical Engineering',
#   'categoria': 'DA',
#   'nr_ore_saptamana': {
#     'curs': 2,
#     'seminar': 0,
#     'proiect': 0,
#     'lucrari': 2
#   },
#   'evaluare': 'E'
# }
```

### Validare (în dezvoltare)

```python
from validators import validate_fisa

# Validează fișa față de planul de învățământ
rezultat = validate_fisa('cale/catre/fisa.docx', 'plan_invatamant.json')
```

## Format Plan de Învățământ

Planul de învățământ trebuie să fie în format JSON:

```json
{
  "discipline": [
    {
      "cod": "IG.IA.202",
      "denumire_ro": "Modelare în ingineria geotenică",
      "denumire_en": "Modelling in Geotechnical Engineering",
      "an": 2,
      "semestru": 3,
      "credite": 5,
      "categoria": "DA",
      "nr_ore_saptamana": {
        "curs": 2,
        "seminar": 0,
        "proiect": 0,
        "lucrari": 2
      },
      "evaluare": "E"
    }
  ]
}
```

## Dependințe

- `python-docx` - Pentru procesarea fișierelor DOCX

## Dezvoltare

### Structura Fișei DOCX

Extractorul se bazează pe structura standard a fișei disciplinei:

- **Tabelul 2 (index 1)**: Date despre disciplină
  - `rows[0].cells[4]`: Denumiri (română / engleză)
  - `rows[1].cells[4]`: Cod disciplină
  - `rows[1].cells[8]`: Categoria
  - `rows[4].cells[6]`: Evaluare

- **Tabelul 3 (index 2)**: Ore pe săptămână
  - `rows[0].cells[4]`: Ore curs
  - `rows[0].cells[8]`: Ore laborator

### Testare

```bash
python extractors.py
```

## Autor

Bogdan Teodoru  
Universitatea Tehnică "Gheorghe Asachi" din Iași

## Licență

MIT
