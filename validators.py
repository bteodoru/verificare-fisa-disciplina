"""
Modul pentru validarea fișelor de disciplină față de planul de învățământ.
"""
import json
from typing import Dict, Any, List
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    """
    Calculează similaritatea între două string-uri (0.0 - 1.0).
    
    Args:
        a: Primul string
        b: Al doilea string
        
    Returns:
        Scor de similaritate între 0.0 și 1.0
    """
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def validate_against_plan(fisa_data: Dict[str, Any], plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validează datele din fișă față de planul de învățământ.
    
    Args:
        fisa_data: Date extrase din fișa disciplinei
        plan_data: Date din planul de învățământ pentru disciplina respectivă
        
    Returns:
        Dicționar cu rezultatele validării
    """
    validari = {}
    
    # 1. Cod disciplină (exact match)
    cod_match = fisa_data['cod'] == plan_data['cod']
    validari['cod'] = {
        'status': 'ok' if cod_match else 'error',
        'valoare_fisa': fisa_data['cod'],
        'valoare_plan': plan_data['cod'],
        'mesaj': None if cod_match else 'Codul disciplinei diferă de cel din plan'
    }
    
    # 2. Denumire română (fuzzy match)
    sim_ro = similarity(fisa_data['denumire_ro'], plan_data['denumire_ro'])
    if sim_ro >= 0.95:
        status_ro = 'ok'
        mesaj_ro = None
    elif sim_ro >= 0.85:
        status_ro = 'warning'
        mesaj_ro = 'Diferențe minore în denumirea în română (probabil diacritice)'
    else:
        status_ro = 'error'
        mesaj_ro = 'Denumirea în română diferă semnificativ de cea din plan'
    
    validari['denumire_ro'] = {
        'status': status_ro,
        'valoare_fisa': fisa_data['denumire_ro'],
        'valoare_plan': plan_data['denumire_ro'],
        'similarity': round(sim_ro, 3),
        'mesaj': mesaj_ro
    }
    
    # 3. Denumire engleză (fuzzy match)
    sim_en = similarity(fisa_data['denumire_en'], plan_data['denumire_en'])
    if sim_en >= 0.95:
        status_en = 'ok'
        mesaj_en = None
    elif sim_en >= 0.85:
        status_en = 'warning'
        mesaj_en = 'Diferențe minore în denumirea în engleză'
    else:
        status_en = 'error'
        mesaj_en = 'Denumirea în engleză diferă semnificativ de cea din plan'
    
    validari['denumire_en'] = {
        'status': status_en,
        'valoare_fisa': fisa_data['denumire_en'],
        'valoare_plan': plan_data['denumire_en'],
        'similarity': round(sim_en, 3),
        'mesaj': mesaj_en
    }
    
    # 4. Categoria (exact match)
    cat_match = fisa_data['categoria'] == plan_data['categoria']
    validari['categoria'] = {
        'status': 'ok' if cat_match else 'error',
        'valoare_fisa': fisa_data['categoria'],
        'valoare_plan': plan_data['categoria'],
        'mesaj': None if cat_match else 'Categoria diferă de cea din plan'
    }
    
    # 5. Credite (exact match)
    credite_match = fisa_data['credite'] == plan_data['credite']
    validari['credite'] = {
        'status': 'ok' if credite_match else 'error',
        'valoare_fisa': fisa_data['credite'],
        'valoare_plan': plan_data['credite'],
        'mesaj': None if credite_match else 'Numărul de credite diferă de cel din plan'
    }
    
    # 6. Ore pe săptămână - detaliate
    ore_fisa = fisa_data['nr_ore_saptamana']
    ore_plan = plan_data['nr_ore_saptamana']
    
    for tip_ore in ['curs', 'seminar', 'proiect', 'lucrari']:
        match = ore_fisa[tip_ore] == ore_plan[tip_ore]
        validari[f'ore_{tip_ore}'] = {
            'status': 'ok' if match else 'error',
            'valoare_fisa': ore_fisa[tip_ore],
            'valoare_plan': ore_plan[tip_ore],
            'mesaj': None if match else f'Ore {tip_ore} diferă de cele din plan'
        }
    
    return validari


def validate_mathematical_constraints(fisa_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validează constrângerile matematice din fișa disciplinei.
    
    Verificări:
    1. total_ore_semestru == credite × 25
    2. total_ore_studiu_individual == studiu_manual + documentare + pregatire_seminarii
    3. total_ore_semestru == total_ore_plan + total_ore_studiu_individual
    
    Args:
        fisa_data: Date extrase din fișa disciplinei
        
    Returns:
        Dicționar cu rezultatele verificărilor matematice
    """
    verificari = {}
    
    # 1. Total ore semestru = credite × 25
    credite = fisa_data['credite']
    total_semestru = fisa_data['total_ore_semestru']
    calculat_din_credite = credite * 25
    
    match_credite = total_semestru == calculat_din_credite
    verificari['total_semestru_din_credite'] = {
        'status': 'ok' if match_credite else 'error',
        'formula': 'total_ore_semestru == credite × 25',
        'valoare_fisa': total_semestru,
        'valoare_calculata': calculat_din_credite,
        'calcul': f'{total_semestru} == {credite} × 25',
        'corect': match_credite,
        'mesaj': None if match_credite else f'Total ore semestru ({total_semestru}) nu este egal cu credite × 25 ({calculat_din_credite})'
    }
    
    # 2. Total ore studiu individual = suma componente
    dist = fisa_data['distributie_fond_timp']
    total_studiu = fisa_data['total_ore_studiu_individual']
    suma_componente = dist['studiu_manual'] + dist['documentare'] + dist['pregatire_seminarii']
    
    match_studiu = total_studiu == suma_componente
    verificari['total_studiu_suma'] = {
        'status': 'ok' if match_studiu else 'error',
        'formula': 'total_studiu == studiu_manual + documentare + pregatire_seminarii',
        'valoare_fisa': total_studiu,
        'valoare_calculata': suma_componente,
        'calcul': f'{total_studiu} == {dist["studiu_manual"]} + {dist["documentare"]} + {dist["pregatire_seminarii"]}',
        'corect': match_studiu,
        'mesaj': None if match_studiu else f'Total ore studiu ({total_studiu}) nu este suma componentelor ({suma_componente})'
    }
    
    # 3. Total ore semestru = total ore plan + total ore studiu individual
    total_plan = fisa_data['total_ore_plan']
    calculat_semestru = total_plan + total_studiu
    
    match_semestru = total_semestru == calculat_semestru
    verificari['total_semestru_suma'] = {
        'status': 'ok' if match_semestru else 'error',
        'formula': 'total_semestru == total_plan + total_studiu',
        'valoare_fisa': total_semestru,
        'valoare_calculata': calculat_semestru,
        'calcul': f'{total_semestru} == {total_plan} + {total_studiu}',
        'corect': match_semestru,
        'mesaj': None if match_semestru else f'Total ore semestru ({total_semestru}) nu este suma ore plan ({total_plan}) + studiu ({total_studiu})'
    }
    
    return verificari


def validate_intervals(fisa_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validează intervalele de valori acceptate.
    
    Verificări:
    1. ore_examinari între 2 și 3
    
    Args:
        fisa_data: Date extrase din fișa disciplinei
        
    Returns:
        Dicționar cu rezultatele verificărilor de interval
    """
    verificari = {}
    
    # Ore examinări între 2 și 3
    examinari = fisa_data['distributie_fond_timp']['examinari']
    in_interval = 2 <= examinari <= 3
    
    verificari['ore_examinari'] = {
        'status': 'ok' if in_interval else 'error',
        'valoare': examinari,
        'interval': [2, 3],
        'corect': in_interval,
        'mesaj': None if in_interval else f'Ore examinări ({examinari}) trebuie să fie între 2 și 3'
    }
    
    return verificari


def validate_fisa(fisa_data: Dict[str, Any], plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Funcția principală de validare a fișei disciplinei.
    
    Args:
        fisa_data: Date extrase din fișa disciplinei
        plan_data: Date din planul de învățământ
        
    Returns:
        Dicționar cu toate rezultatele validării
    """
    print(fisa_data)
    # Găsește disciplina în plan după cod
    disciplina_plan = None
    for disc in plan_data['discipline']:
        if disc['cod'] == fisa_data['cod']:
            disciplina_plan = disc
            break
    
    if not disciplina_plan:
        return {
            'status': 'error',
            'cod': fisa_data['cod'],
            'mesaj': f"Disciplina cu codul {fisa_data['cod']} nu există în planul de învățământ",
            'validari': None
        }
    
    # Rulează toate validările
    validari_plan = validate_against_plan(fisa_data, disciplina_plan)
    validari_matematice = validate_mathematical_constraints(fisa_data)
    validari_intervale = validate_intervals(fisa_data)
    
    # Determină status-ul global
    toate_validarile = {**validari_plan, **validari_matematice, **validari_intervale}
    
    are_erori = any(v.get('status') == 'error' for v in toate_validarile.values())
    are_warning = any(v.get('status') == 'warning' for v in toate_validarile.values())
    
    if are_erori:
        status_global = 'error'
        summary = 'Fișa conține erori care trebuie corectate'
    elif are_warning:
        status_global = 'warning'
        summary = 'Fișa este validă dar conține avertismente'
    else:
        status_global = 'success'
        summary = 'Fișa este validă și conformă cu planul de învățământ'
    
    # Construiește rezultatul final
    rezultat = {
        'status': status_global,
        'cod': fisa_data['cod'],
        'denumire': fisa_data['denumire_ro'],
        'validari': {
            'comparatie_plan': validari_plan,
            'verificari_matematice': validari_matematice,
            'verificari_intervale': validari_intervale
        },
        'summary': summary,
        'statistici': {
            'total_verificari': len(toate_validarile),
            'succes': sum(1 for v in toate_validarile.values() if v.get('status') == 'ok'),
            'warning': sum(1 for v in toate_validarile.values() if v.get('status') == 'warning'),
            'erori': sum(1 for v in toate_validarile.values() if v.get('status') == 'error')
        }
    }
    
    return rezultat


def load_plan_invatamant(file_path: str) -> Dict[str, Any]:
    """
    Încarcă planul de învățământ din fișier JSON.
    
    Args:
        file_path: Calea către fișierul JSON cu planul
        
    Returns:
        Dicționar cu datele din plan
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    # Test pe fișa încărcată
    from extractors import extract_fisa_disciplina
    
    fisa_path = '/mnt/user-data/uploads/IGIA202_Modelare_in__ingineria_geotehnica_Teodoru_2.docx'
    plan_path = 'plan_invatamant.json'
    
    print("Extrag datele din fișă...")
    fisa_data = extract_fisa_disciplina(fisa_path)
    
    print("Încarc planul de învățământ...")
    plan_data = load_plan_invatamant(plan_path)
    
    print("\nValidez fișa față de plan...\n")
    rezultat = validate_fisa(fisa_data, plan_data)
    
    print("="*70)
    print(f"STATUS: {rezultat['status'].upper()}")
    print(f"Cod: {rezultat['cod']}")
    print(f"Denumire: {rezultat['denumire']}")
    print("="*70)
    
    print(f"\n📊 STATISTICI:")
    stats = rezultat['statistici']
    print(f"  Total verificări: {stats['total_verificari']}")
    print(f"  ✓ Succes: {stats['succes']}")
    print(f"  ⚠ Warning: {stats['warning']}")
    print(f"  ✗ Erori: {stats['erori']}")
    
    print(f"\n💬 SUMMARY: {rezultat['summary']}")
    
    # Afișează detalii validări
    print("\n" + "="*70)
    print("DETALII VALIDĂRI")
    print("="*70)
    
    for categorie, validari in rezultat['validari'].items():
        print(f"\n📋 {categorie.upper().replace('_', ' ')}:")
        for nume, detalii in validari.items():
            status_icon = {'ok': '✓', 'warning': '⚠', 'error': '✗'}.get(detalii['status'], '?')
            print(f"  {status_icon} {nume}: {detalii['status']}")
            if detalii.get('mesaj'):
                print(f"     → {detalii['mesaj']}")
    
    print("\n" + "="*70)
    
    # Output JSON complet
    print("\n📄 OUTPUT JSON COMPLET:")
    print(json.dumps(rezultat, indent=2, ensure_ascii=False))