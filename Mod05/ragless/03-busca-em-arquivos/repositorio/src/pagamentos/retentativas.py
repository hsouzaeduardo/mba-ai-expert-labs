"""Retentativas com espera exponencial para as chamadas ao gateway de pagamento."""
import time
import urllib.error

MAX_TENTATIVAS = 3  # a primeira chamada e mais duas
ESPERA_INICIAL_MS = 500  # dobra a cada nova tentativa: 500 ms e depois 1.000 ms
CODIGOS_REPETIVEIS = {502, 503, 504}  # erros temporários do gateway; erro 4xx nunca se repete


def com_retentativas(chamada):
    """Executa a chamada e repete só nos erros HTTP 502, 503 e 504, com espera exponencial."""
    espera_ms = ESPERA_INICIAL_MS
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            return chamada()
        except urllib.error.HTTPError as erro:
            if erro.code not in CODIGOS_REPETIVEIS or tentativa == MAX_TENTATIVAS:
                raise
            time.sleep(espera_ms / 1000)
            espera_ms *= 2
