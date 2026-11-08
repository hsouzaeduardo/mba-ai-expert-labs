"""Agente de Vagas: Microsoft Agent Framework (MAF) + Microsoft Foundry + MCP público da Triagen.

Front-end (DevUI):  devui entidades --port 8080 --instrumentation
Terminal:           python terminal.py

Os cinco componentes do slide 15, na ordem em que aparecem neste arquivo:
  1. Modelo ............ FoundryChatClient -> deployment do projeto no Microsoft Foundry
  2. Instruções ........ comum/instrucoes.md (o mesmo texto do agente ADK)
  3. Ferramentas ....... MCPStreamableHTTPTool -> servidor MCP da Triagen
  4. Memória/contexto .. AgentSession (histórico da conversa; memória longa é o Capítulo 7)
  5. Política .......... comum/politica.json -> allowlist, aprovação e limites do laço
"""

from __future__ import annotations

import os
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path

from agent_framework import Agent, FunctionInvocationContext, MCPStreamableHTTPTool, function_middleware
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

PASTA_MAF = Path(__file__).resolve().parents[2]  # agente-vagas/maf
sys.path.insert(0, str(PASTA_MAF.parent / "comum"))  # governança compartilhada com o ADK

from governanca import (  # noqa: E402
    FERRAMENTAS_COM_APROVACAO,
    FERRAMENTAS_PERMITIDAS,
    FERRAMENTAS_SEM_APROVACAO,
    INSTRUCOES,
    LIMITES,
    MCP_URL,
    registrar_auditoria,
)

load_dotenv(PASTA_MAF / ".env")

# Slide 17: em dev o agente age como VOCÊ (a conta do `az login`): é a "chave emprestada".
# Em produção troque por Managed Identity ou identidade de agente no Entra.
IDENTIDADE = "AzureCliCredential (usuário do az login)"

# 1. MODELO --------------------------------------------------------------------
# Slide 18: o laço precisa de limite, timeout e disjuntor. No MAF isso mora no cliente.
cliente = FoundryChatClient(
    project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    model=os.getenv("FOUNDRY_MODEL"),
    credential=AzureCliCredential(),
    function_invocation_configuration={
        "max_iterations": LIMITES["max_chamadas_modelo"],
        "max_function_calls": LIMITES["max_chamadas_ferramenta"],
        "max_duration_seconds": LIMITES["max_segundos"],
    },
)

# 3. FERRAMENTAS + 5. POLÍTICA ---------------------------------------------------
# Um único objeto aponta para o servidor MCP; a política é aplicada ferramenta a ferramenta.
triagen = MCPStreamableHTTPTool(
    name="triagen",
    url=MCP_URL,
    description="Vagas de emprego públicas da plataforma Triagen",
    allowed_tools=FERRAMENTAS_PERMITIDAS,  # slides 26 e 27: lista de permissão
    approval_mode={
        "always_require_approval": FERRAMENTAS_COM_APROVACAO,  # slide 28: escreve -> aprovação ligada
        "never_require_approval": FERRAMENTAS_SEM_APROVACAO,
        "default": "always_require",  # o que a política não classificou pede aprovação (falha segura)
    },
    load_prompts=False,  # o servidor não publica prompts
    request_timeout=60,
)


# Slides 26 e 28: trilha de auditoria. Middleware de função roda em toda execução de ferramenta.
# Uma chamada que espera aprovação só chega aqui depois de aprovada; rejeitada, nunca executa.
@function_middleware
async def auditoria(context: FunctionInvocationContext, call_next: Callable[[], Awaitable[None]]) -> None:
    nome = context.function.name
    try:
        await call_next()
    except Exception:
        registrar_auditoria("maf", nome, context.arguments, "erro", identidade=IDENTIDADE)
        raise
    registrar_auditoria("maf", nome, context.arguments, "executada", context.result, identidade=IDENTIDADE)


# O DevUI procura uma variável chamada `agent` neste pacote.
agent = Agent(
    client=cliente,
    name="agente_vagas",
    description="Encontra vagas de emprego no MCP público da Triagen (MAF + Foundry)",
    instructions=INSTRUCOES,  # 2. INSTRUÇÕES
    tools=[triagen],
    middleware=[auditoria],
)
