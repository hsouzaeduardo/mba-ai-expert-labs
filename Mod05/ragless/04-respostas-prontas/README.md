# 04 — Respostas prontas: o FAQ aprovado antes da pergunta

Notebook: `demo-respostas-prontas.ipynb`

## O que mostra

A linha **Respostas prontas** do slide 18 ("RAGless: cada variante tira uma peça do pipeline clássico"): na ingestão, o LLM gera pares pergunta-resposta; na consulta, a busca vetorial devolve a resposta pronta. É o FAQ fechado e auditável de regulamento, política e atendimento. O que sai do pipeline clássico aqui é o **LLM na hora da consulta**: a busca vetorial continua. Se o slide 18 ainda disser "Sem vetor" nesta linha, leia pela descrição da própria linha (o rótulo foi trocado com o da Árvore).

1. **Ingestão:** o LLM lê três políticas do acervo (descanso remunerado, viagens e reembolso, cartão corporativo), uma chamada por documento, e devolve de 4 a 6 pares num formato fixo (structured outputs), cada um com o `id` do trecho que o sustenta.
2. **Curadoria auditável:** os pares aprovados vão para `respostas_aprovadas.json`, nesta pasta.
3. **Vetorização:** só as perguntas aprovadas viram vetor, numa matriz numpy normalizada.
4. **Consulta sem LLM:** um embedding por pergunta, o cosseno com as perguntas aprovadas e um limiar (0,6) que decide entre a resposta pronta e o encaminhamento ao atendimento.
5. **Custo e previsibilidade:** a mesma pergunta, três vezes, dá a mesma resposta, sem nenhum token de geração.

Não usa o Azure AI Search: os pares ficam num arquivo JSON e a comparação é feita com numpy. Em produção, eles morariam num índice (no AI Search, por exemplo), e a consulta continuaria sem chamar um LLM.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de chat que aceite structured outputs (por exemplo, `gpt-5-mini` ou `gpt-4.1`), usado só na ingestão, e um deployment de embedding (`text-embedding-3-small` no `.env.example`).
- Nenhum outro recurso. Este notebook não depende do índice de `tipos-de-rag`.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL` e `AZURE_OPENAI_EMBEDDING_DIMENSIONS`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem. A pasta de trabalho precisa ser a do notebook (o padrão do Jupyter e do VS Code): é nela que o arquivo de curadoria é gravado.
3. A primeira execução grava `respostas_aprovadas.json`. Nas seguintes, a Execução 1 chama o LLM de novo, só para mostrar a ingestão, mas a consulta usa o arquivo já aprovado. Se a Execução 1 falhar no dia (cota ou nome do deployment de chat) com o arquivo já gravado, rode as células seguintes mesmo assim: a consulta só usa o deployment de embedding, e a conta da Execução 5 sai sem os tokens da ingestão. Não pule a célula da Execução 1: as seguintes usam as listas que ela cria antes de chamar o LLM. Sem o arquivo, a Execução 2 para em vez de gravar um FAQ pela metade.

## O que observar

- Cada par aponta o trecho de origem: é a rastreabilidade do FAQ.
- Paráfrases tendem a ficar acima do limiar, e perguntas fora do escopo, abaixo. Olhe a coluna de similaridade: 0,6 é só um ponto de partida, a calibrar com perguntas reais e com o modelo de embedding que você usa.
- Para ver a curadoria em ação, mude um `"aprovada"` para `false` no arquivo e rode de novo a partir da Execução 2: aquele par sai da consulta, e a pergunta parecida passa a ser encaminhada ou, se outra pergunta aprovada passar do limiar, recebe a resposta dela. Reprovar um par não bloqueia o assunto: para isso, mantenha a pergunta e aprove como resposta um encaminhamento.
- A mesma pergunta dá sempre a mesma resposta, porque ela é lida do arquivo, e não gerada.

## Limpeza

Nada a apagar no Azure: o notebook não cria recursos. O `respostas_aprovadas.json` é o artefato de auditoria e fica nesta pasta. Apague-o para gerar e aprovar o FAQ de novo, por exemplo depois de mudar uma política, ou antes da aula, se quiser que a curadoria seja a do dia.
