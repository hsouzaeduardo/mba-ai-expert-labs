# 02 — Árvore de seções: o modelo navega pelo sumário até a seção certa

Notebook: `demo-arvore-de-secoes.ipynb`

## O que mostra

A linha **Árvore (PageIndex)** do slide 18 e a linha **Árvore de seções** do slide 19, **sem vetor e sem índice de busca**: na ingestão, o LLM gera um sumário hierárquico da norma de segurança da informação da Contoso Industrial (`Cap05/acervo/ti/norma-de-seguranca-da-informacao.md`, 8 seções e 22 subseções numeradas); na consulta, navega por ele e abre a seção certa. O slide diz quando isso cabe: documento longo e estruturado, como contrato, norma ou relatório. Para caber na aula, a norma é curta (~1.500 tokens), e a Execução 4 mostra quando a técnica se paga. Se o slide 18 ainda disser "Sem LLM na consulta" nesta linha, leia pela descrição: o LLM trabalha na consulta, e o que sai é o vetor (o rótulo foi trocado com o de Respostas prontas).

1. **Ingestão, parte determinística:** os títulos numerados viram uma árvore (id pela numeração, título, nível, texto próprio e filhos), sem chamar o modelo.
2. **Ingestão, parte com LLM:** uma chamada `responses.parse` (structured outputs, classes `ResumoSecao` e `Sumario`) escreve um resumo de uma frase por seção. A árvore com os resumos fica em `arvore.json`, ao lado do notebook.
3. **Navegar e abrir a seção certa:** o modelo lê só o sumário e devolve 1 ou 2 seções, com justificativa (classe `Navegacao`). O código confere os ids (só os da árvore, sem repetir, no máximo dois) e abre o texto completo das seções; o modelo responde citando `[seção X.Y]`. Perguntas e seções esperadas: chatbot gratuito (4.2), prazo para reportar incidente (6.1) e dados fora do Brasil (7.2). O gabarito fica no código, para a tabela; o modelo não o recebe.
4. **Quanto custou:** sumário + seções abertas contra o documento inteiro (~1.500 tokens, `o200k_base`) e os tokens cobrados nas duas chamadas de cada pergunta, com a parte lida do cache de prompt.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de chat que aceite **structured outputs**, por exemplo `gpt-5-mini` (versão 2025-08-07). A lista de modelos está na página de structured outputs do Microsoft Learn.
- Não usa Azure AI Search, embedding nem índice. Não depende do notebook `tipos-de-rag/00-indice-compartilhado`.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` e `AZURE_OPENAI_DEPLOYMENT`. As variáveis de embedding e do AI Search não são lidas.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem.
3. A 1ª execução faz a chamada de ingestão e grava o `arvore.json`; as seguintes leem o arquivo e fazem só as duas chamadas por pergunta. Para mostrar a ingestão ao vivo, apague o `arvore.json` antes da aula. Se a norma mudar, apague-o também: o sumário precisa ser gerado de novo.

## O que observar

- **Execução 1:** as seções `##` não têm texto próprio; abrir uma delas é abrir todas as subseções.
- **Execução 2:** o sumário (id, título e resumo) é tudo o que o modelo vê na consulta para escolher a seção. Se ele pular ou inventar um id, o notebook avisa.
- **Execução 3:** compare "o modelo escolheu", "seções abertas" e "seção esperada". O modelo pode abrir uma segunda seção ou o capítulo inteiro; se errar a seção, a resposta erra junto, mas o caminho e a justificativa ficam na tabela.
- **Execução 4:** a norma é curta, então o sumário pode ficar perto do tamanho dela e a economia de texto tende a ser pequena, ou nenhuma, com duas chamadas por pergunta. Instruções + sumário tendem a passar de 1.024 tokens, o mínimo do cache de prompt: da 2ª pergunta em diante, a coluna "em cache" tende a mostrar parte da entrada lida do cache, cobrada com desconto (sem garantia). Isso vale para os modelos do GPT-4o até a família GPT-5.5, como o `gpt-5-mini`; da família GPT-5.6 em diante, o cache funciona por pontos de corte (veja `../01-contexto-longo`), e a coluna pode ficar em 0. A árvore se paga em documento longo: o sumário cresce com o número de seções, não com o tamanho delas.
- Os resumos mudam a cada geração do sumário (apague o `arvore.json` para gerar de novo); as seções escolhidas e as respostas, a cada execução. A árvore da Execução 1 e os tokens do documento não mudam.

## Limpeza

Nada a apagar no Azure: este notebook não cria recursos. O único arquivo criado é o `arvore.json`, nesta pasta; apague-o quando quiser gerar o sumário de novo.
