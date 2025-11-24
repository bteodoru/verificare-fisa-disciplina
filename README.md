# Verificare Fișe Disciplină

Sistem automatizat pentru verificarea conformității fișelor de disciplină cu planul de învățământ.

## Descriere

Acest proiect extrage automat datele din fișele de disciplină (format DOCX) și le compară cu planul de învățământ pentru a identifica inconsistențe.

## Funcționalități

- ✅ Extragere automată din fișe DOCX (16 câmpuri)
- ✅ Comparație cu planul de învățământ
- ✅ Verificări matematice automate
- ✅ Detectare diferențe (exact match + fuzzy matching)
- ✅ Raportare detaliată în format JSON

## Structura Proiectului

```
verificare-fisa/
├── extractors.py           # Extracție date din DOCX (16 câmpuri)
├── validators.py           # Validare față de plan (13 verificări)
├── test_validators.py      # Suite de teste pentru validators
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
#   'credite': 5,
#   'nr_ore_saptamana_total': 4,
#   'nr_ore_saptamana': {
#     'curs': 2,
#     'seminar': 0,
#     'proiect': 0,
#     'lucrari': 2
#   },
#   'total_ore_plan': 56,
#   'distributie_fond_timp': {
#     'studiu_manual': 20,
#     'documentare': 25,
#     'pregatire_seminarii': 24,
#     'examinari': 2
#   },
#   'total_ore_studiu_individual': 69,
#   'total_ore_semestru': 125,
#   'evaluare': 'E'
# }
```

### Validare (în dezvoltare)

```python
from validators import validate_fisa

# Validează fișa față de planul de învățământ
rezultat = validate_fisa('cale/catre/fisa.docx', 'plan_invatamant.json')
```

### Validare față de plan - Complet

```python
from validators import validate_fisa, load_plan_invatamant
from extractors import extract_fisa_disciplina

# Extrage date din fișă
fisa_data = extract_fisa_disciplina('fisa.docx')

# Încarcă planul de învățământ
plan_data = load_plan_invatamant('plan_invatamant.json')

# Validează
rezultat = validate_fisa(fisa_data, plan_data)

# Verifică status
if rezultat['status'] == 'success':
    print("✓ Fișa este validă!")
elif rezultat['status'] == 'warning':
    print("⚠ Fișa are avertismente")
else:
    print("✗ Fișa conține erori")

# Afișează statistici
stats = rezultat['statistici']
print(f"Verificări: {stats['succes']}/{stats['total_verificari']}")
```

## Tipuri de Verificări

### 1. Comparație cu Planul (9 verificări)

- ✓ Cod disciplină (exact match)
- ✓ Denumire română (fuzzy match: similarity ≥ 0.95)
- ✓ Denumire engleză (fuzzy match: similarity ≥ 0.95)
- ✓ Categoria (DA/DOP/DOB/DFA)
- ✓ Credite
- ✓ Ore curs
- ✓ Ore seminar
- ✓ Ore proiect
- ✓ Ore laborator

### 2. Verificări Matematice (3 verificări)

- ✓ `total_ore_semestru == credite × 25`
  - Exemplu: `125 == 5 × 25 ✓`
- ✓ `total_ore_studiu == studiu_manual + documentare + pregatire_seminarii`
  - Exemplu: `69 == 20 + 25 + 24 ✓`
- ✓ `total_ore_semestru == total_ore_plan + total_ore_studiu_individual`
  - Exemplu: `125 == 56 + 69 ✓`

### 3. Verificări Intervale (1 verificare)

- ✓ Ore examinări între 2 și 3
  - Exemplu: `2 ≤ 2 ≤ 3 ✓`

**Total: 13 verificări automate**

## Output Validare

```json
{
  "status": "success|warning|error",
  "cod": "IG.IA.202",
  "denumire": "Modelare în ingineria geotenică",
  "validari": {
    "comparatie_plan": {
      "cod": {"status": "ok", "valoare_fisa": "...", "valoare_plan": "..."},
      "denumire_ro": {"status": "ok", "similarity": 0.984, ...},
      ...
    },
    "verificari_matematice": {
      "total_semestru_din_credite": {
        "status": "ok",
        "formula": "total_ore_semestru == credite × 25",
        "calcul": "125 == 5 × 25",
        "corect": true
      },
      ...
    },
    "verificari_intervale": {
      "ore_examinari": {"status": "ok", "interval": [2, 3], ...}
    }
  },
  "statistici": {
    "total_verificari": 13,
    "succes": 13,
    "warning": 0,
    "erori": 0
  },
  "summary": "Fișa este validă și conformă cu planul de învățământ"
}
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
      "nr_ore_saptamana_total": 4,
      "nr_ore_saptamana": {
        "curs": 2,
        "seminar": 0,
        "proiect": 0,
        "lucrari": 2
      },
      "total_ore_plan": 56,
      "distributie_fond_timp": {
        "studiu_manual": 20,
        "documentare": 25,
        "pregatire_seminarii": 24,
        "examinari": 2
      },
      "total_ore_studiu_individual": 69,
      "total_ore_semestru": 125,
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

- **Tabelul 3 (index 2)**: Ore pe săptămână și distribuție timp
  - `rows[0].cells[1]`: Total ore pe săptămână
  - `rows[0].cells[4]`: Ore curs
  - `rows[0].cells[8]`: Ore laborator
  - `rows[1].cells[1]`: Total ore din planul de învățământ
  - `rows[3].cells[12]`: Ore studiu manual
  - `rows[4].cells[12]`: Ore documentare
  - `rows[5].cells[12]`: Ore pregătire seminarii
  - `rows[6].cells[12]`: Ore examinări
  - `rows[8].cells[1]`: Total ore studiu individual
  - `rows[9].cells[1]`: Total ore pe semestru
  - `rows[10].cells[1]`: Număr credite

### Testare

```bash
python extractors.py
```

## Autor

Bogdan Teodoru  
Universitatea Tehnică "Gheorghe Asachi" din Iași

## Licență

MIT
