import socket, json, time, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [TCP Server] %(levelname)s: %(message)s")
HOST, PORT, BUF = '127.0.0.1', 9000, 1024
def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT)); s.listen(1); logging.info(f"Ouvindo em {HOST}:{PORT}")
        conn, addr = s.accept()
        with conn:
            logging.info(f"Conectado a {addr}"); total, t0, n = 0, time.time(), 0
            while True:
                try:
                    data = conn.recv(BUF)
                    if not data: break
                    total += len(data); n += 1
                    p = json.loads(data.decode('utf-8'))
                    rtt = round((time.time() - p.get('client_ts', time.time())) * 1000, 2)
                    conn.sendall(json.dumps({"status": "ok", "rtt_ms": rtt}).encode())
                    logging.info(f"Msg #{n} | RTT: {rtt}ms | {len(data)}B")
                except Exception as e: logging.error(e); break
            logging.info(f"Fim. Throughput: {round(total/(time.time()-t0),2)} B/s | {n} msgs")
if __name__ == "__main__": start()