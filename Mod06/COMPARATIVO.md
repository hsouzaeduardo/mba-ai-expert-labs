# MAF × ADK: o mesmo agente em dois runtimes

Instruções, política e auditoria são **as mesmas** (`comum/`). O que muda é só a fiação em cada `agent.py`.
É o argumento do slide 25 visto em código: como a ferramenta fala MCP, você troca o runtime sem trocar o catálogo de ferramentas.

| Conceito (slide) | MAF + Microsoft Foundry | ADK + Gemini | O que observar |
|---|---|---|---|
| **Modelo** (S15) | `FoundryChatClient` + nome do *deployment* no projeto: `maf/entidades/agente_vagas/agent.py:47` | Nome do modelo em `model=`: `adk/agente_vagas/agent.py:80` | No Foundry o modelo é um recurso do projeto, com cota, filtro de conteúdo e RBAC. No ADK é um nome; Vertex AI traz a governança equivalente. |
| **Instruções** (S15) | `instructions=INSTRUCOES` (`agent.py:93`) | `instruction=INSTRUCOES` (`agent.py:82`) | Mesmo arquivo `comum/instrucoes.md`. Pegadinha do ADK: `{texto}` na instrução vira injeção de estado da sessão. |
| **Ferramentas via MCP** (S24, S25) | Um `MCPStreamableHTTPTool` (`agent.py:60`) | Dois `McpToolset` no mesmo servidor (`agent.py:50` e `:54`) | No MAF a política é por ferramenta; no ADK a confirmação vale por toolset, então a política vira dois toolsets. |
| **Lista de permissão** (S26, S27) | `allowed_tools` (`agent.py:64`) | `tool_filter` (`agent.py:52` e `:56`) | Ferramenta nova publicada no servidor não entra sozinha em nenhum dos dois. |
| **Aprovação no que escreve** (S12, S13, S28) | `approval_mode` por nome + `"default": "always_require"` (`agent.py:66-68`) | `require_confirmation=True` (`agent.py:57`) | O padrão do MAF ainda é *não* pedir aprovação; aqui declaramos `default: always_require`, então ferramenta não classificada pede aprovação. Política é o que você declara, não o que o framework assume. O ADK aceita um *callable* sobre os argumentos, o que permite aprovação condicional (ex.: só acima de um valor, como o estorno do slide 13). |
| **Humano no laço, no código** | `resposta.user_input_requests` + `pedido.to_function_approval_response(bool)`: `maf/terminal.py:30-36` | Evento `adk_request_confirmation` + `FunctionResponse` com `{"confirmed": bool}` | O ADK já traz isso pronto no terminal (`adk run`). No MAF o `terminal.py` faz o papel. |
| **Limite do laço** (S18) | No **cliente**: `max_iterations`, `max_function_calls`, `max_duration_seconds` (`agent.py:51`) | No **runtime**: `adk web --max_llm_calls 8` ou `ADK_MAX_LLM_CALLS` | No MAF o limite viaja com o agente. No ADK depende de como ele é executado, e o teto exposto é de chamadas ao modelo. |
| **Auditoria** (S26, S28) | *Function middleware* (`agent.py:77`): registra só execuções; uma chamada rejeitada nunca chega lá | `after_tool_callback` (`agent.py:63`): vê também a pausa (`aguardando_aprovacao`) e a rejeição (`rejeitada`) | As duas gravam em `logs/auditoria.jsonl`, com dado pessoal mascarado (`comum/governanca.py:40`). |
| **Rastreamento** (S26) | `devui ... --instrumentation`: OpenTelemetry com eventos de trace no DevUI; em produção, Application Insights | `adk web` traz a aba Trace; em produção, Cloud Trace | É o "reconstituir a decisão do agente" da última linha do slide 26. |
| **Identidade** (S17) | `AzureCliCredential` (`agent.py:50`): em dev, o agente age como **você** | `GOOGLE_API_KEY`: uma chave compartilhada, sem sujeito | Os dois exemplos usam a "chave emprestada" do slide 17. Em produção: Managed Identity ou identidade de agente no Entra; no Google, service account no Vertex AI. Pegadinha do ADK: ao conectar em qualquer MCP ele tenta mTLS e, para isso, carrega o login padrão do gcloud da máquina, mesmo usando API key. Desligamos com `GOOGLE_API_USE_CLIENT_CERTIFICATE=false` no `.env`. |
| **Memória e contexto** (S15) | `AgentSession` | `SessionService` (em memória no `adk web`) | Só histórico da conversa. Memória longa é o Capítulo 7. |
| **Front de desenvolvimento** | DevUI: acha a variável `agent` na pasta `entidades/`; aprovação com botões; token de acesso por padrão | `adk web`: acha `root_agent`; confirmação, trace e avaliação na mesma tela | Os dois são para desenvolvimento, não para usuário final. |
| **Hospedagem** (S16) | Hosted agent no Foundry (você traz o runtime) ou prompt agent (declara o MCP no portal, sem código) | Vertex AI Agent Engine ou Cloud Run | Este código é material de *hosted agent*. |
| **Multiagente** (S20) | `agent-framework-orchestrations` | `SequentialAgent`, `ParallelAgent`, `LoopAgent`, `sub_agents` | **Não usado de propósito** (S7, S22): um agente com ferramentas resolve. Subir de degrau exige motivo escrito. |
| **Instalação** | `mcp` e `tenacity` são opcionais no core (extra `all`); sem eles a conexão MCP falha | `google-adk[mcp]` | Os dois mudam rápido: `requirements.txt` está com versões fixas. |

## Leitura para a aula

- **O que é igual vale mais do que o que é diferente.** Política, instruções e trilha de auditoria ficaram fora do framework. Trocar de runtime custou dois arquivos de ~100 linhas.
- **Onde mora o limite diz quem responde por ele.** No MAF o teto do laço vai junto com o agente. No ADK, quem executa decide.
- **Aprovação por nome × aprovação por argumento.** O `default: always_require` que declaramos no MAF protege contra ferramenta nova. O callable do ADK protege contra valor alto. O slide 12 pede os dois: classificar por custo de desfazer, não por "lê ou escreve".
- **Nenhum dos dois resolve identidade em dev.** O slide 17 continua valendo: sem identidade própria, quem assina é quem fez o `az login` ou quem gerou a chave.
