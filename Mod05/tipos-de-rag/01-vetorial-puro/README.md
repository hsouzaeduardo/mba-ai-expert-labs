# 01 — RAG vetorial puro: o primeiro degrau

Notebook: `demo-vetorial-puro.ipynb`

## O que mostra

A busca **vetorial pura** no Azure AI Search, testada com as seis perguntas do slide 14 ("O primeiro degrau: por que busca vetorial pura não basta"). É a linha **Vetorial puro** do slide 15: uma consulta, similaridade de embedding, o menor custo.

1. **Busca vetorial pura:** a pergunta vira vetor no cliente, com o mesmo deployment e a mesma dimensão da indexação, e o índice devolve os 5 vizinhos mais próximos.
2. **As seis perguntas do slide 14**, com o gabarito de `acervo/perguntas.json`: posição do trecho certo e scores do 1º e do 2º colocados.
3. **Lupa nos empates:** projetos ATLAS x ÓRION x HÉLIOS e SKU 48213-B x C x D.
4. **RAG completo:** resposta com citação a partir dos 3 primeiros trechos. Quando a resposta erra, o erro nasce na recuperação (slide 29).

## Pré-requisitos no Azure

- O índice `cap05-acervo`, criado pelo notebook `../00-indice-compartilhado`. Se ele não existir, a célula de configuração para com uma mensagem clara.
- **Azure OpenAI** com o mesmo deployment de embedding usado no notebook 00 e um deployment de chat (por exemplo, `gpt-5-mini`).
- **Azure AI Search:** o mesmo serviço do notebook 00. Este notebook só consulta e não cria nada.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` (os mesmos valores do notebook 00), `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução.

## Como rodar

1. Rode antes o notebook 00. Uma vez basta: o índice fica no serviço.
2. Abra este notebook e execute todas as células, em ordem.

## O que observar

- O vetor tende a acertar linguagem natural, paráfrase e sinônimo, e a tropeçar em código de norma, sigla interna e string exata.
- Mesmo quando acerta, o 1º e o 2º colocados quase empatam nas seções parecidas. **Esse empate é a lição.**
- Na Execução 4, confira a linha "O trecho certo está entre eles?" antes de julgar a resposta do modelo.
- Os números mudam com o modelo e a dimensão do embedding. Por isso o notebook mostra posições e scores: a lição aparece mesmo quando a sorte ajuda o vetor.
- O remédio é a busca híbrida, no notebook `../02-hibrido`.

## Limpeza

Nada a apagar: este notebook não cria recursos. O índice é apagado pela célula de limpeza do notebook 00.
