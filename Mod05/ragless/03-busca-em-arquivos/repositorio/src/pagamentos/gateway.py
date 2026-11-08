"""Cliente do gateway de pagamento do banco parceiro: envia as ordens de pagamento a fornecedores."""
import json
import urllib.error
import urllib.request

from .retentativas import com_retentativas

# Rede de segurança: só vale quando a chave gateway.timeout_segundos falta no arquivo do ambiente.
# O valor de produção fica em config/producao.yaml (ver docs/adr-007-timeout-do-gateway.md).
TIMEOUT_PADRAO = 15


def obter_timeout(config: dict) -> float:
    """Timeout de cada chamada ao gateway, em segundos."""
    return config.get("gateway", {}).get("timeout_segundos", TIMEOUT_PADRAO)


def enviar_ordem(config: dict, ordem: dict) -> dict:
    """Envia uma ordem ao gateway. A chave de idempotência evita pagamento em dobro numa retentativa."""
    requisicao = urllib.request.Request(
        f"{config['gateway']['url']}/ordens",
        data=json.dumps(ordem).encode("utf-8"),
        headers={"Content-Type": "application/json", "Idempotency-Key": ordem["id"]},
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=obter_timeout(config)) as resposta:
        return json.loads(resposta.read())


def processar_ordem(config: dict, ordem: dict) -> str:
    """Envia a ordem, com retentativas, e devolve o status final dela."""
    try:
        com_retentativas(lambda: enviar_ordem(config, ordem))
        return "ENVIADA"
    except urllib.error.HTTPError as erro:
        return "FALHA_GATEWAY" if erro.code >= 500 else "REJEITADA"
    except (TimeoutError, urllib.error.URLError):
        # Timeout do nosso lado não entra nas retentativas: a ordem fica para reprocessamento.
        return "FALHA_GATEWAY"
