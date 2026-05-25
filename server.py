import sqlite3
import json
import time
import logging
import asyncio
import random
import hashlib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

app = FastAPI(title="Projeto Redes - Monitoramento")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY, timestamp REAL, device_id TEXT, 
        temperature REAL, humidity REAL, rtt_ms REAL, alert TEXT)""")
    conn.commit()
    conn.close()
    logging.info("Banco inicializado.")

init_db()

def hash_pwd(p): return hashlib.sha256(p.encode()).hexdigest()

@app.post("/api/register")
async def register(d: dict):
    u, p = d.get("username"), d.get("password")
    if not u or not p: raise HTTPException(400, "Campos obrigatorios")
    try:
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (u, hash_pwd(p)))
        conn.commit(); conn.close()
        return {"status": "cadastrado"}
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Usuario ja existe")

@app.post("/api/login")
async def login(d: dict):
    u, p = d.get("username"), d.get("password")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username=?", (u,))
    row = c.fetchone(); conn.close()
    if row and row[0] == hash_pwd(p):
        return {"status": "ok", "token": hash_pwd(f"{u}_{time.time()}")}
    raise HTTPException(401, "Credenciais invalidas")

@app.post("/api/data")
async def receive_data(d: dict, req: Request):
    token = req.headers.get("Authorization", "")
    if not token: raise HTTPException(401, "Token ausente")
    try:
        ts_client = d.get("client_ts", time.time())
        rtt = round((time.time() - ts_client) * 1000, 2)
        temp = d.get("temperature", 0)
        alert = "ALTA_TEMPERATURA" if temp > 28 else None
        if alert: logging.warning(f"ALERTA: {temp}°C no device {d.get('device_id')}")
        conn = sqlite3.connect(DB); c = conn.cursor()
        c.execute("INSERT INTO sensor_data VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                  (time.time(), d.get("device_id","unknown"), temp, d.get("humidity",0), rtt, alert))
        conn.commit(); conn.close()
        return {"status": "ok", "rtt_ms": rtt}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/api/history")
async def history(limit: int = 50):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall(); conn.close()
    return [{"id":r[0],"ts":r[1],"dev":r[2],"temp":r[3],"hum":r[4],"rtt":r[5],"alert":r[6]} for r in rows]

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept(); logging.info("WS conectado")
    task = asyncio.create_task(_stream(ws))
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: logging.info("WS desconectado")
    finally: task.cancel()

async def _stream(ws: WebSocket):
    while True:
        await asyncio.sleep(2)
        temp = round(random.uniform(20, 32), 2)
        hum = round(random.uniform(40, 75), 2)
        payload = {"dev":"sim_01", "temp":temp, "hum":hum, "ts":time.time()}
        await ws.send_text(json.dumps(payload))
        if temp > 28: logging.warning(f"WS ALERTA: {temp}°C")

@app.get("/")
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)