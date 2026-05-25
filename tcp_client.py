import socket, json, time, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [TCP Client] %(levelname)s: %(message)s")
HOST, PORT, BUF = '127.0.0.1', 9000, 1024
def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT)); logging.info("Conectado ao TCP Server")
        for i in range(10):
            ts = time.time()
            s.sendall(json.dumps({"id":i,"dev":"tcp_01","temp":25.0,"hum":60.0,"client_ts":ts}).encode())
            try:
                resp = json.loads(s.recv(BUF).decode())
                logging.info(f"Msg {i+1}/10 | RTT local: {round((time.time()-ts)*1000,2)}ms | Servidor: {resp.get('rtt_ms')}ms")
            except Exception as e: logging.error(e); break
            time.sleep(1)
        logging.info("Teste TCP concluído.")
if __name__ == "__main__": start()