import fastapi
import requests

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Kerrotaan FastAPI:lle, että HTML-sivut ovat "templates"-kansiossa
templates = Jinja2Templates(directory="templates")

# Tämä reitti näyttää verkkosivusi, kun menet osoitteeseen http://127.0.0.1:8000
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Tämä reitti ottaa vastaan suojatun datan verkkosivulta
@app.post("/submit-exam")
async def receive_answers(data: dict):
    print("Vastaanotettu suojattu data verkkosivulta:", data)
    return {"status": "Success", "message": "Vastaukset lähetetty onnistuneesti taustajärjestelmään!"}
