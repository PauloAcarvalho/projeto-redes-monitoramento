import socket, json, time, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [UDP Client] %(levelname)s: %(message)s")
HOST, PORT, BUF = '127.0.0.1', 9001, 1024
def start():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2); logging.info("Iniciando teste UDP")
        for i in range(10):
            ts = time.time()
            s.sendto(json.dumps({"id":i,"dev":"udp_01","temp":25.0,"client_ts":ts}).encode(), (HOST, PORT))
            try:
                resp, _ = s.recvfrom(BUF)
                r = json.loads(resp.decode())
                logging.info(f"Msg {i+1}/10 | RTT: {round((time.time()-ts)*1000,2)}ms | Servidor: {r.get('rtt_ms')}ms")
            except socket.timeout: logging.warning(f"Msg {i+1} PERDIDA (timeout)")
            time.sleep(1)
        logging.info("Teste UDP concluído.")
if __name__ == "__main__": start()