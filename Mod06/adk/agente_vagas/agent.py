"""Agente de Vagas: Google Agent Development Kit (ADK) + Gemini + MCP público da Triagen.

Front-end (adk web):  adk web --port 8000 --max_llm_calls 8      (rodar dentro da pasta adk/)
Terminal:             adk run agente_vagas

Os cinco componentes do slide 15, na ordem em que aparecem neste arquivo:
  1. Modelo ............ Gemini, pelo nome do modelo (GOOGLE_MODEL no .env)
  2. Instruções ........ comum/instrucoes.md (o mesmo texto do agente MAF)
  3. Ferramentas ....... McpToolset -> servidor MCP da Triagen
  4. Memória/contexto .. Session do runner (histórico da conversa; memória longa é o Capítulo 7)
  5. Política .......... comum/politica.json -> allowlist, confirmação; o limite do laço fica no runtime
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext

PASTA_ADK = Path(__file__).resolve().parents[1]  # agente-vagas/adk
sys.path.insert(0, str(PASTA_ADK.parent / "comum"))  # governança compartilhada com o MAF

from governanca import (  # noqa: E402
    FERRAMENTAS_COM_APROVACAO,
    FERRAMENTAS_SEM_APROVACAO,
    INSTRUCOES,
    MCP_URL,
    registrar_auditoria,
)

# Slide 17: com GOOGLE_API_KEY o agente usa uma chave compartilhada, não um sujeito auditável.
# Em produção (Vertex AI / Agent Engine) troque por service account ou identidade de agente.
IDENTIDADE = "GOOGLE_API_KEY (chave compartilhada)"


def _conexao() -> StreamableHTTPConnectionParams:
    return StreamableHTTPConnectionParams(url=MCP_URL, timeout=30)


# 3. FERRAMENTAS + 5. POLÍTICA ---------------------------------------------------
# No ADK, `require_confirmation` vale para o toolset inteiro (o callable recebe os argumentos,
# não o nome da ferramenta). Por isso a política vira DOIS toolsets no mesmo servidor MCP.
# Juntos, os dois `tool_filter` formam a lista de permissão dos slides 26 e 27.
ferramentas_leitura = McpToolset(
    connection_params=_conexao(),
    tool_filter=FERRAMENTAS_SEM_APROVACAO,
)
ferramentas_irreversiveis = McpToolset(
    connection_params=_conexao(),
    tool_filter=FERRAMENTAS_COM_APROVACAO,
    require_confirmation=True,  # slide 28: escreve -> aprovação ligada
)


# Slides 26 e 28: trilha de auditoria. No ADK o callback também vê a pausa e a rejeição,
# porque a ferramenta "responde" pedindo confirmação antes de executar.
def auditoria(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: Any) -> None:
    status = "executada"
    erro = tool_response.get("error") if isinstance(tool_response, dict) else None
    if isinstance(erro, str):
        if "requires confirmation" in erro:
            status = "aguardando_aprovacao"
        elif "rejected" in erro:
            status = "rejeitada"
        else:
            status = "erro"
    registrar_auditoria("adk", tool.name, args, status, tool_response, identidade=IDENTIDADE)
    return None  # None = não altera a resposta da ferramenta


# O `adk web` procura uma variável chamada `root_agent` neste pacote.
root_agent = Agent(
    name="agente_vagas",
    model=os.getenv("GOOGLE_MODEL", "gemini-3.5-flash"),  # 1. MODELO
    description="Encontra vagas de emprego no MCP público da Triagen (ADK + Gemini)",
    instruction=INSTRUCOES,  # 2. INSTRUÇÕES
    tools=[ferramentas_leitura, ferramentas_irreversiveis],
    after_tool_callback=auditoria,
)
