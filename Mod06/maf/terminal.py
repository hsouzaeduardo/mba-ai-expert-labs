"""Conversa com o agente MAF pelo terminal, tratando a aprovação humana no código.

O DevUI faz isso com botões. Aqui fica visível o que acontece por baixo:
o framework PAUSA o laço e devolve um pedido de aprovação em vez de executar a ferramenta.

Uso (dentro da pasta maf/):  python terminal.py
"""

from __future__ import annotations

import asyncio

from agent_framework import Message

from entidades.agente_vagas import agent


async def main() -> None:
    async with agent:  # abre e fecha a conexão com o servidor MCP
        sessao = agent.create_session()  # 4. MEMÓRIA/CONTEXTO: o histórico vive na sessão
        print("Agente de Vagas (MAF + Microsoft Foundry). Linha vazia ou Ctrl+C para sair.\n")
        while True:
            pergunta = input("você> ").strip()
            if not pergunta:
                break

            resposta = await agent.run(pergunta, session=sessao)

            # Slide 28: humano no laço por exceção. Só a ferramenta irreversível cai aqui.
            while resposta.user_input_requests:
                decisoes = []
                for pedido in resposta.user_input_requests:
                    chamada = pedido.function_call
                    print(f"\n[APROVAÇÃO NECESSÁRIA] {chamada.name}({chamada.arguments})")
                    aprovado = input("Aprovar esta ação irreversível? [s/N] ").strip().lower() == "s"
                    decisoes.append(pedido.to_function_approval_response(aprovado))
                resposta = await agent.run(Message("user", decisoes), session=sessao)

            print(f"\nagente> {resposta.text}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
