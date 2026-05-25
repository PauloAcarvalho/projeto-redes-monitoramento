import socket, json, time, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [UDP Server] %(levelname)s: %(message)s")
HOST, PORT, BUF = '127.0.0.1', 9001, 1024
def start():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT)); logging.info(f"Ouvindo UDP em {HOST}:{PORT}")
        total, t0, n = 0, time.time(), 0
        while True:
            try:
                data, addr = s.recvfrom(BUF)
                total += len(data); n += 1
                p = json.loads(data.decode('utf-8'))
                rtt = round((time.time() - p.get('client_ts', time.time())) * 1000, 2)
                s.sendto(json.dumps({"status": "ok", "rtt_ms": rtt}).encode(), addr)
                logging.info(f"De {addr} | Msg #{n} | RTT: {rtt}ms | {len(data)}B")
            except Exception as e: logging.error(e); break
        logging.info(f"Fim. Throughput: {round(total/(time.time()-t0),2)} B/s")
if __name__ == "__main__": start()