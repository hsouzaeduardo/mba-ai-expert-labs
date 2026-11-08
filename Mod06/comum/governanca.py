"""Governança compartilhada pelos dois agentes (MAF e ADK).

Tudo o que NÃO depende de framework mora aqui: instruções, política de ferramentas,
limites do laço e trilha de auditoria. O agent.py de cada framework só faz a fiação.
É isso que permite dizer que é "o mesmo agente" rodando em dois runtimes.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent

# Componente 2 do slide 15: instruções. Sem chaves no texto, porque o ADK
# interpreta {variavel} como injeção de estado da sessão.
INSTRUCOES: str = (PASTA / "instrucoes.md").read_text(encoding="utf-8")

# Componente 5 do slide 15: política como artefato versionado, não como if espalhado no código.
POLITICA: dict[str, Any] = json.loads((PASTA / "politica.json").read_text(encoding="utf-8"))

MCP_URL: str = POLITICA["mcp_url"]
LIMITES: dict[str, int] = POLITICA["limites"]
FERRAMENTAS: dict[str, dict[str, Any]] = POLITICA["ferramentas"]

# Slides 26 e 27: lista de permissão. Ferramenta nova publicada no servidor não entra sozinha.
FERRAMENTAS_PERMITIDAS: list[str] = list(FERRAMENTAS)
# Slides 12 e 28: o que custa caro desfazer nasce com aprovação ligada.
FERRAMENTAS_COM_APROVACAO: list[str] = [n for n, f in FERRAMENTAS.items() if f["exige_aprovacao"]]
FERRAMENTAS_SEM_APROVACAO: list[str] = [n for n, f in FERRAMENTAS.items() if not f["exige_aprovacao"]]

ARQUIVO_AUDITORIA = RAIZ / "logs" / "auditoria.jsonl"
_CAMPOS_PESSOAIS = {"full_name", "email", "phone", "linkedin_url", "cv_url"}


def _mascarar(valor: Any) -> str:
    """Log de auditoria não pode virar vazamento de dado pessoal (LGPD)."""
    texto = str(valor)
    if "@" in texto:
        usuario, dominio = texto.split("@", 1)
        return f"{usuario[:1]}***@{dominio}"
    return f"{texto[:2]}***" if texto else ""


def _tamanho(resultado: Any) -> int:
    """Quantos caracteres a ferramenta devolveu: é isso que vai para o contexto (slide 18)."""
    if resultado is None:
        return 0
    if isinstance(resultado, (list, tuple)):
        return sum(_tamanho(item) for item in resultado)
    texto = getattr(resultado, "text", None)  # Content do MAF
    if isinstance(texto, str):
        return len(texto)
    return len(json.dumps(resultado, ensure_ascii=False, default=str))  # dict do ADK


def _como_dict(argumentos: Any) -> dict[str, Any]:
    if hasattr(argumentos, "model_dump"):
        argumentos = argumentos.model_dump()
    return dict(argumentos) if isinstance(argumentos, Mapping) else {"valor": str(argumentos)}


def registrar_auditoria(
    framework: str,
    ferramenta: str,
    argumentos: Any,
    status: str,
    resultado: Any = None,
    identidade: str = "",
) -> None:
    """Uma linha por chamada de ferramenta: data, identidade, ferramenta, argumentos e desfecho (slide 28)."""
    args = {k: (_mascarar(v) if k in _CAMPOS_PESSOAIS and v else v) for k, v in _como_dict(argumentos).items()}
    linha = {
        "data": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "framework": framework,
        "identidade": identidade,
        "responsavel_operacional": POLITICA["responsavel_operacional"],
        "politica_versao": POLITICA["versao"],
        "ferramenta": ferramenta,
        "efeito": FERRAMENTAS.get(ferramenta, {}).get("efeito", "desconhecido"),
        "status": status,
        "argumentos": args,
        "caracteres_no_contexto": _tamanho(resultado),
    }
    ARQUIVO_AUDITORIA.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO_AUDITORIA.open("a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")
