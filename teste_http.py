import urllib.request
import urllib.error
import json
import time

ts = time.time()
payload = {
    "device_id": "teste_debug",
    "temperature": 25.0,
    "humidity": 60.0,
    "client_ts": ts
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    "http://localhost:8000/api/data",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": "token_qualquer"  # Token simples para bypass do check
    },
    method="POST"
)

try:
    response = urllib.request.urlopen(req)
    print("✅ Sucesso:", response.read().decode())
except urllib.error.HTTPError as e:
    print(f"❌ Erro HTTP {e.code}: {e.reason}")
    print("📄 Resposta do servidor:", e.read().decode())
except Exception as e:
    print(f"❌ Erro inesperado: {type(e).__name__}: {e}")