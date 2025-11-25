"""
FastAPI application pentru verificarea fișelor de disciplină.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import tempfile
import os
import json
from pathlib import Path

from extractors import extract_fisa_disciplina
from validators import validate_fisa, load_plan_invatamant

# Inițializare FastAPI
app = FastAPI(
    title="Verificare Fișe Disciplină",
    description="Sistem automatizat pentru verificarea conformității fișelor de disciplină",
    version="1.0.0"
)

# Setup templates și static files
templates = Jinja2Templates(directory="templates")

# Creează directoare necesare
Path("static/uploads").mkdir(parents=True, exist_ok=True)

# Încarcă planul de învățământ o singură dată (la startup)
plan_data = load_plan_invatamant('plan_invatamant.json')


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Pagina principală cu interfața de upload și validare.
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "discipline": plan_data['discipline']
    })


@app.get("/api/discipline")
async def get_discipline():
    """
    Returnează lista de discipline din planul de învățământ.
    
    Returns:
        Lista de discipline cu cod și denumire
    """
    discipline_list = [
        {
            "cod": disc["cod"],
            "denumire_ro": disc["denumire_ro"],
            "an": disc.get("an", "N/A"),
            "semestru": disc.get("semestru", "N/A"),
            "credite": disc.get("credite", "N/A")
        }
        for disc in plan_data['discipline']
    ]
    return {"discipline": discipline_list}


@app.post("/api/extract")
async def extract_fisa(file: UploadFile = File(...)):
    """
    Extrage datele din fișa DOCX încărcată.
    
    Args:
        file: Fișierul DOCX încărcat
        
    Returns:
        Datele extrase din fișă (16 câmpuri)
    """
    # Verifică extensia fișierului
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="Fișierul trebuie să fie în format DOCX"
        )
    
    # Salvează temporar fișierul
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extrage datele
        fisa_data = extract_fisa_disciplina(tmp_path)
        
        # Șterge fișierul temporar
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "data": fisa_data
        }
        
    except Exception as e:
        # Șterge fișierul temporar dacă există
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la extragerea datelor: {str(e)}"
        )


@app.post("/api/validate")
async def validate_fisa_endpoint(
    file: UploadFile = File(...), 
    cod_disciplina: str = Form(None)
):
    """
    Validează fișa DOCX încărcată față de planul de învățământ.
    
    Args:
        file: Fișierul DOCX încărcat
        cod_disciplina: Codul disciplinei din plan (opțional - se folosește codul din fișă dacă nu e furnizat)
        
    Returns:
        Rezultatul validării cu toate verificările
    """
    # Verifică extensia fișierului
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="Fișierul trebuie să fie în format DOCX"
        )
    
    # Salvează temporar fișierul
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extrage datele din fișă
        fisa_data = extract_fisa_disciplina(tmp_path)
        
        # Șterge fișierul temporar
        os.unlink(tmp_path)
        
        # Dacă utilizatorul a selectat manual o disciplină, suprascrie codul din fișă
        if cod_disciplina:
            fisa_data['cod'] = cod_disciplina
        
        # Validează față de plan
        rezultat = validate_fisa(fisa_data, plan_data)
        
        return {
            "status": "success",
            "filename": file.filename,
            "cod_selectat_manual": cod_disciplina is not None,
            "validare": rezultat
        }
        
    except Exception as e:
        # Șterge fișierul temporar dacă există
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la validare: {str(e)}"
        )


@app.get("/api/plan")
async def get_plan():
    """
    Returnează întregul plan de învățământ.
    
    Returns:
        Planul complet de învățământ
    """
    return plan_data


@app.get("/health")
async def health_check():
    """
    Endpoint pentru verificarea stării aplicației.
    """
    return {
        "status": "healthy",
        "discipline_count": len(plan_data['discipline']),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)