# 02 — Onde o vetor mora: Azure Cosmos DB for NoSQL

Notebook: `demo-cosmos-db.ipynb`

## O que mostra

O vetor guardado **no mesmo item** que o texto e os metadados, num contêiner do Azure Cosmos DB for NoSQL, com busca por similaridade em SQL (`VectorDistance`) e o RAG completo no fim. É a linha **Cosmos DB for NoSQL** da tabela do slide 22: "Dado operacional e vetor juntos, com atualização contínua".

- **Slides 20 e 21:** a pergunta que decide onde o vetor mora é se o dado muda em tempo real, não qual banco é o melhor.
- **Slide 22:** dimensões (505 a 4.096, conforme o tipo de índice), índices `flat`, `quantizedFlat` e `diskANN`, reranking.
- **Slide 23:** onde o DiskANN entraria (acima de ~50 mil vetores: recall alto, memória baixa e lida bem com dado que muda) e o trade-off de sempre: recall, memória e tempo de indexação. Aqui o índice é `quantizedFlat`.
- **Slide 14:** o quase empate do SKU 48213-B continua, qualquer que seja a base.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de embedding (`text-embedding-3-small` no `.env.example`) e um deployment de chat (por exemplo, `gpt-5-mini`).
- **Azure Cosmos DB for NoSQL**, conta provisionada (manual ou autoscale) ou serverless, com o recurso **Vector Search for NoSQL API** habilitado. Prefira o portal: *Settings* → *Features* → *Vector Search for NoSQL API* → *Enable*. A aprovação é automática, mas pode levar até 15 minutos. Habilite **antes da aula**.
- Pela CLI: `az cosmosdb update --resource-group <grupo> --name <conta> --capabilities EnableNoSQLVectorSearch`. Cuidado: `--capabilities` substitui a lista **inteira** de capacidades da conta. Confira antes com `az cosmosdb show --resource-group <grupo> --name <conta> --query capabilities` e repita as que já existem (se a lista trouxer `EnableServerless`: `--capabilities EnableServerless EnableNoSQLVectorSearch`).
- O notebook cria o banco `cap05` **sem throughput compartilhado** (a busca vetorial não funciona nesse modo) e o contêiner `trechos`: chave de partição `/doc_id`, política vetorial (`/embedding`, `float32`, `cosine`, `EMBEDDING_DIMENSIONS`) e índice `quantizedFlat`.
- A **chave primária** da conta (*Keys*, no portal): é ela que permite criar banco e contêiner pelo SDK. Em produção, prefira Microsoft Entra ID com um papel de dados (*Cosmos DB Built-in Data Contributor*) e crie banco e contêiner pelo plano de controle (portal, Bicep ou CLI).

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS`, `AZURE_COSMOS_ENDPOINT` (formato `https://<conta>.documents.azure.com:443/`) e `AZURE_COSMOS_KEY`.

Copie `Cap05/.env.example` para `Cap05/.env` e preencha. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem. Ele não depende dos notebooks de `tipos-de-rag`: gera os próprios vetores.
3. Rodar de novo é seguro: o contêiner existente é reaproveitado e os itens são regravados pelo mesmo `id`, sem duplicar.

## O que observar

- **Execução 2:** a política vetorial e o índice `quantizedFlat`, como o serviço registrou. O `flat` não serve para 1.536 dimensões (máximo de 505).
- **Execução 3:** 50 itens no contêiner e o custo da carga em RUs. O Learn estima ~35 RUs por inserção com vetor de 1.536 dimensões; numa conta com 400 RU/s, o SDK absorve as respostas 429 sozinho e a célula só demora mais.
- **Execução 4:** com `cosine`, o `VectorDistance` já devolve a similaridade (−1 a 1, maior = mais parecido). O SKU 48213-B continua quase empatado com o 48213-C e o 48213-D.
- **Execução 5:** a resposta com citação, igual à dos outros notebooks: o modelo não sabe onde o vetor mora.
- Com menos de 1.000 vetores, `quantizedFlat` e `diskANN` ainda não entram em ação: o Cosmos DB faz varredura completa, e a busca pode custar mais RUs.

## Limpeza

Com `APAGAR_RECURSOS = True`, a última célula apaga o contêiner `trechos`, que o notebook criou. O banco `cap05` só é apagado se ficar vazio; outros contêineres dele não são tocados. Numa conta provisionada, o contêiner cobra o RU/s reservado mesmo sem uso: apague no fim da aula.

Mudou a dimensão do embedding no `.env`? Reinicie o kernel (o notebook lê o `.env` só uma vez): a política vetorial não se altera no lugar, e a Execução 2 para com um erro. Apague o contêiner com a limpeza e rode o notebook de novo, com `APAGAR_RECURSOS` de volta em `False`. Mudou só o modelo, com a mesma dimensão? Nada falha: reinicie o kernel e rode o notebook inteiro, para regravar os 50 vetores com o modelo novo.
