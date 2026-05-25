# Protocolo de Aplicação - Monitoramento em Tempo Real

## 1. Visão Geral
Sistema cliente-servidor para coleta, persistência e visualização de dados de sensores em tempo real. Utiliza HTTP/REST para cadastro/autenticação/histórico, WebSocket para streaming em tempo real, e sockets TCP/UDP puros para análise de métricas de rede.

## 2. Formato das Mensagens
JSON UTF-8.
**Cliente → Servidor:**
{"device_id": "sim_01", "temperature": 24.5, "humidity": 55.0, "client_ts": 1716580000.123}
**Servidor → Cliente:**
{"status": "ok", "rtt_ms": 2.15, "server_ts": 1716580000.125}

## 3. Portas e Serviços
| Serviço | Porta | Protocolo | Função |
|---------|-------|-----------|--------|
| API REST + WS | 8000 | HTTP/1.1 + WebSocket | Cadastro, login, histórico, dashboard |
| Teste TCP | 9000 | TCP (raw socket) | Métricas com garantia de entrega |
| Teste UDP | 9001 | UDP (raw socket) | Métricas sem garantia, baixa latência |

## 4. Métricas
- **RTT:** `timestamp_servidor - timestamp_cliente` (enviado no payload)
- **Throughput:** `bytes_totais_recebidos / tempo_total_sessao`
- **Alerta:** Disparado automaticamente quando `temperature > 28°C`

## 5. Fluxo de Comunicação
1. Cliente autentica via POST /api/login → recebe token.
2. Envia dados via POST /api/data com header Authorization.
3. Servidor persiste em SQLite, calcula RTT, loga e responde.
4. WebSocket mantém canal aberto enviando JSON a cada 2s para o dashboard.
5. Sockets TCP/UDP rodam em paralelo para comparação de desempenho e captura Wireshark.