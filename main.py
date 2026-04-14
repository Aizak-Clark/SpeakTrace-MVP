import json
import os
from typing import Optional
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_FILE = "data.json"

# Функция загрузки данных из файла
def load_db():
    if not os.path.exists(DB_FILE):
        # Начальные данные, если файла еще нет (соответствует ПР-03)
        return [
            {
                "id": 1, 
                "title": "Демо-презентация", 
                "date": "2026-04-10", 
                "purity": 85, 
                "source": "Live", 
                "duration": 10,
                "transcript": "Привет! Это пример текста, который уже был в системе."
            },
        ]
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Функция сохранения данных в файл
def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Инициализируем данные при старте
db_sessions = load_db()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"sessions": db_sessions}
    )

@app.get("/add", response_class=HTMLResponse)
async def add_page(request: Request):
    return templates.TemplateResponse(request=request, name="add_session.html", context={})

@app.post("/add")
async def add_session(
    title: str = Form(...), 
    source: str = Form(...), 
    duration: int = Form(...),
    manual_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    final_text = ""
    if file and file.filename:
        content = await file.read()
        final_text = content.decode("utf-8")
    elif manual_text:
        final_text = manual_text

    # 1. Считаем количество вхождений мусорных слов для имитации ИИ
    parasite_count = final_text.lower().count("типа") + \
                     final_text.lower().count("как бы") + \
                     final_text.lower().count("э-э")

    # 2. Рассчитываем динамический процент чистоты
    # Допустим, каждое такое слово отнимает 5% от идеальных 100%
    calculated_purity = 100 - (parasite_count * 5)
    
    # Чтобы процент не ушел в минус
    if calculated_purity < 0: calculated_purity = 0

    # 3. Применяем подсветку (теги <mark>)
    processed_text = final_text.replace("типа", "<mark class='parasite'>типа</mark>") \
                               .replace("как бы", "<mark class='parasite'>как бы</mark>") \
                               .replace("э-э", "<mark class='hesitation'>э-э</mark>")

    new_id = max([s["id"] for s in db_sessions]) + 1 if db_sessions else 1
    
    new_session = {
        "id": new_id,
        "title": title,
        "date": "2026-04-14",
        "purity": calculated_purity,  # ТЕПЕРЬ ТУТ ДИНАМИКА
        "source": source,
        "duration": duration,
        "transcript": processed_text
    }
    
    db_sessions.append(new_session)
    save_db(db_sessions)
    return RedirectResponse(url="/", status_code=303)

@app.get("/report/{session_id}", response_class=HTMLResponse)
async def report(request: Request, session_id: int):
    # Поиск сессии по ID
    session = next((s for s in db_sessions if s["id"] == session_id), None)
    if not session:
        return HTMLResponse(content="Сессия не найдена", status_code=404)
    
    return templates.TemplateResponse(
        request=request, 
        name="report.html", 
        context={"session": session}
    )