# 03 — Busca em arquivos: o agente que procura como um dev

Notebook: `demo-busca-em-arquivos.ipynb` · Repositório explorado pelo agente: `repositorio/`

## O que mostra

A linha **Busca em arquivos** do slide 19 ("RAGless: recuperar sem banco vetorial, e quando isso cabe"). Sem índice, sem embedding e sem banco vetorial, um agente responde perguntas sobre uma base de código: lista pastas, procura termos e abre arquivos, como um dev faria.

1. **As ferramentas na mão:** `listar_pasta`, `procurar_termo` e `ler_arquivo`, chamadas sem o modelo, mostram exatamente o que o agente recebe. A busca por `tempo limite` não acha nada, porque é literal, e o pedido de `../../../.env` é recusado.
2. **Timeout de produção:** o agente separa os 8 s de `config/producao.yaml` dos 15 s de `TIMEOUT_PADRAO`, que só valem se a chave faltar, e dos 30 s de homologação, citando `arquivo:linha`.
3. **Erro 504:** o termo exato leva à seção certa do runbook, entre seções quase iguais (401, 422, 502 ou 503, 504).
4. **Custo:** chamadas ao modelo e tokens por pergunta. O custo migra para a consulta.

O `repositorio/` é um serviço fictício de pagamento a fornecedores da Contoso Industrial (`servico-pagamentos`), com sete arquivos: README, duas configurações, dois módulos Python, um runbook de incidentes e uma ADR.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de chat que aceite chamada de funções na Responses API (por exemplo, `gpt-5-mini`). O notebook usa a v1 API (`https://<recurso>.openai.azure.com/openai/v1/`).
- Mais nada: este exemplo não usa AI Search, embedding nem banco de dados.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT` (no formato `https://<recurso>.openai.azure.com`), `AZURE_OPENAI_API_KEY` e `AZURE_OPENAI_DEPLOYMENT`.

Copie `Cap05/.env.example` para `Cap05/.env` e preencha. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem. A Execução 4 usa o consumo registrado nas Execuções 2 e 3.
3. Cada pergunta faz várias chamadas ao modelo, uma depois da outra: conte com mais tempo do que numa chamada única.
4. Não edite a pasta `repositorio/`: as perguntas e as falas da aula dependem dos números plantados nela.
5. Antes da aula, rode o notebook inteiro uma vez no seu deployment: é o que confirma que o serviço aceita o reenvio dos pedidos de ferramenta na forma mínima, sem `id` e sem o raciocínio do modelo. Se a segunda chamada de uma pergunta voltar com erro 400, troque esse reenvio, em `executar_agente`, por `entrada += resposta.output` e acrescente `include=["reasoning.encrypted_content"]` à chamada `responses.create`: é a forma que o Learn recomenda para modelos de raciocínio sem estado.

## O que observar

- O rastro de cada pergunta (`passo N | ferramenta {argumentos} → resultado`) é a recuperação acontecendo na hora da consulta. O caminho muda de uma execução para outra; a conclusão não deveria mudar.
- A resposta cita `[arquivo:linha]`, e cada número pode ser conferido abrindo o arquivo.
- As ferramentas são só de leitura e validam o caminho no código (`caminho_seguro`), que recusa caminho absoluto antes de tocar o disco: quem escolhe os argumentos é o modelo, e o conteúdo dos arquivos também é entrada não confiável.
- Na Execução 4, os tokens de entrada crescem a cada passo, porque o laço reenvia a lista inteira (`store=False`). A coluna "em cache" pode ficar em zero: o prompt caching só entra a partir de 1.024 tokens de começo idêntico. Essa é a regra dos modelos do GPT-4o até a família GPT-5.5, como o `gpt-5-mini`; da família GPT-5.6 em diante, o cache funciona por pontos de corte (veja `../01-contexto-longo`), e os números da coluna mudam.
- O raciocínio do modelo não volta na lista, então é refeito e cobrado a cada passo. Em modelos de raciocínio, a Microsoft recomenda reenviá-lo (cifrado, no modo sem estado), o que gasta menos tokens; o notebook mostra a forma mínima e explica a diferença.

## Limpeza

Nada a apagar: este notebook não cria recursos no Azure.
